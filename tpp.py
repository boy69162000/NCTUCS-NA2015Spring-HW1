import re
import time
import string
import socket
import win32com.client, win32api, win32con
shell = win32com.client.Dispatch("WScript.Shell")
twitchHost = "irc.twitch.tv"
twitchPort = 6667
twitchPass = "" #your twitch cauth code
twitchNick = "" #your twitch id
twitchChan = "" # #(yourTwitchID)
#twitchChan = "#twitchplayspokemon" #for sample inputs
twitchs=socket.socket()
twitchs.connect((twitchHost, twitchPort))
twitchs.setblocking(0)
#mode = "democracy"
mode = "anarchy"
totalinput = 0
execinput = 0
starttime = time.time()
logtime = starttime+60
demodl = -1
tenscntdwn = 0
demoinputs = {}
demovotes = {}
VK_CODE = { "a":0x5A,
            "b":0x58,
            "up":0x55,
            "down":0x4A,
            "left":0x48,
            "right":0x4B,
            "start":0x4F,
            "select":0x50 }
#Numpad
#a='z', b='x', up/down/left/right='u/j/h/k', start='o', select='p'
def press(inputs):
    shell.AppActivate("VisualBoyAdvance")
    if inputs == "wait":
        time.sleep(0.2)
    else:
        win32api.keybd_event(VK_CODE[inputs], 0, 0, 0)
        time.sleep(0.2)
        win32api.keybd_event(VK_CODE[inputs],0 , win32con.KEYEVENTF_KEYUP ,0)
    if mode == "democracy":
        time.sleep(1)

twitchs.send(bytes("PASS %s\r\n" % twitchPass, "UTF-8"))
twitchs.send(bytes("NICK %s\r\n" % twitchNick, "UTF-8"))
twitchs.send(bytes("USER %s %s twitch :%s\r\n" % (twitchNick, twitchHost, twitchNick), "UTF-8"))
twitchs.send(bytes("JOIN %s\r\n" % twitchChan, "UTF-8"))
#twitchs.send(bytes("PRIVMSG %s :a\r\n" % twitchChan, "UTF-8"))
while True:
    nowsec = time.time()
    if nowsec > logtime:
        day = (nowsec-starttime)//86400
        hour = (nowsec-starttime)//3600-day*24
        minute = (nowsec-starttime)//60-day*1440-hour*60
        second = (nowsec-starttime)-day*86400-hour*3600-minute*60
        print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Play time:",int(day),"d",int(hour),"h",int(minute),"m",int(second),"s, {:>8} inputs with {:>8} executed ***".format(totalinput, execinput))
        logtime = nowsec+60

    if mode == "democracy":
        if demodl == -1:
            demodl = nowsec+25
            print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Next input in less than 25s ***")
        elif nowsec >= demodl:
            resultk = ""
            resultv = 0
            eqmax = 0
            for k in demoinputs.keys():
                if demoinputs[k] > resultv:
                    resultk = k
                    resultv = demoinputs[k]
                    eqmax = 0
                elif demoinputs[k] == resultv:
                    eqmax = 1
            if resultv == 0 or eqmax == 1:
                print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Input: N/A ***")
            else:
                x = 0
                inputs = "wait"
                print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Input:",resultk,"with",resultv,"votes ***")
                execinput += 1
                while x < len(resultk):
                    times = 1
                    if resultk[x] == "a" or resultk[x] == "b":
                        inputs = resultk[x]
                        x += 1
                    elif resultk[x:x+2] == "up":
                        inputs = resultk[x:x+2]
                        x += 2
                    elif resultk[x:x+4] == "wait" or resultk[x:x+4] == "down" or resultk[x:x+4] == "left":
                        inputs = resultk[x:x+4]
                        x += 4
                    elif resultk[x:x+5] == "right" or resultk[x:x+5] == "start":
                        inputs = resultk[x:x+5]
                        x += 5
                    elif resultk[x:x+6] == "select":
                        inputs = resultk[x:x+4]
                        x += 6
                    else:
                        x += 1
                        print("WAAAAH?")
                    if x < len(resultk):
                        if resultk[x].isdigit():
                            times = int(resultk[x])
                            x += 1
                    while times > 0:
                        press(inputs)
                        times -= 1
                    if x >= len(resultk):
                        break

            demoinputs.clear()
            demovotes.clear()
            demodl = time.time()+25
            tenscntdwn = 0
            print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Next input in less than 25s ***")
        elif demodl-nowsec <= 10 and tenscntdwn == 0:
            print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Next input in less than 10s ***")
            tenscntdwn = 1

    try:
        stream = twitchs.recv(65536).decode("UTF-8")
    except socket.error:
        continue
        
    buff = stream.split("\n")
    stream = buff.pop()

    for line in buff:
        line = line.strip()
        if line[0:4] == "PING":
            twitchs.send(bytes("PONG :%s\r\n" % line[6:], "UTF-8"))
            #print("PING replied")
            continue
        elif len(line.split()) != 4:
            continue

        temp = line.split("!")[0]
        user = temp[1:].capitalize()
        if len(user) >= 4:
            msg = line.split()[3].lower()
            anarRE = re.search("\A:a\Z|\A:b\Z|\A:up\Z|\A:down\Z|\A:left\Z|\A:right\Z|\A:start\Z|\A:select\Z", msg)
            demoRE = re.search("\A:((a|b|up|down|left|right|start|select|wait)[2-9]?){1,9}\Z", msg)
            commRE = re.search("\A:!anarchy\Z|\A:!democracy\Z", msg)
            if user == "" and commRE != None: #fill blank string with streamer id
                if mode != msg[1:]:
                    print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Mode switched to", msg[2:],"***")
                    mode = msg[2:]
                    if mode == "democracy":
                        nowsec = time.time()
                        demodl = nowsec+25
                        tenscntdwn = 0
                        print(time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime()),"   *** Next input in less than 25s ***")
            elif mode == "anarchy" and anarRE != None:
                inputs = msg[1:]
                totalinput += 1
                press(inputs)
                execinput += 1
                print("{:>25} {:<25} {}".format(user,inputs,time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime())))
            elif mode == "democracy" and demoRE != None:
                inputs = msg[1:]
                commandlist = re.findall("a[2-9]?|b[2-9]?|up[2-9]?|down[2-9]?|left[2-9]?|right[2-9]?|start[2-9]?|select[2-9]?|wait[2-9]?", inputs)
                commandlen = 0
                for command in commandlist:
                    if command[-1].isdigit():
                        commandlen += int(command[-1])
                    else:
                        commandlen += 1
                if commandlen > 9:
                    continue
                elif inputs in demoinputs:
                    demoinputs[inputs] += 1
                else:
                    demoinputs.update({inputs: 1})
                totalinput += 1
                if user in demovotes:
                    demoinputs[demovotes[user]] -= 1
                    demovotes[user] = inputs
                else:
                    demovotes.update({user: inputs})
                print("{:>25} {:<25} {}".format(user,inputs,time.strftime("%y/%m/%d %H:%M:%S GMT",time.gmtime())))
