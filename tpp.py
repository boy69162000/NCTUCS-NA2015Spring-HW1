import re
import time
import string
import socket
twitchHost = "irc.twitch.tv"
twitchPort = 6667
twitchPass = "oauth:hdwhjcb84q8ukcbin0jt3jwj17moyo"
twitchNick = "boy69162000"
#twitchChan = "#boy69162000"
twitchChan = "#twitchplayspokemon"
twitchs=socket.socket()
twitchs.connect((twitchHost, twitchPort))
twitchs.setblocking(0)
"""
    address = "irc.twitch.tv";
    chatnet = "twitch";
    port = "6667";
    password = "oauth:hdwhjcb84q8ukcbin0jt3jwj17moyo";
    name = "#twitchplayspokemon";

    ---MESSAGE FORMAT---
    :wahisietel_the_cake!wahisietel_the_cake@wahisietel_the_cake.tmi.twitch.tv PRIVMSG #twitchplayspokemon :up
"""
twitchs.send(bytes("PASS %s\r\n" % twitchPass, "UTF-8"))
twitchs.send(bytes("NICK %s\r\n" % twitchNick, "UTF-8"))
twitchs.send(bytes("USER %s %s twitch :%s\r\n" % (twitchNick, twitchHost, twitchNick), "UTF-8"))
twitchs.send(bytes("JOIN %s\r\n" % twitchChan, "UTF-8"))
#twitchs.send(bytes("PRIVMSG %s :a\r\n" % twitchChan, "UTF-8"))
#mode = "anarchy"
mode = "democracy"
demodl = -1
tenscntdwn = 0
demoinputs = {}
while 1:
    if mode == "democracy":
        nowsec = time.time()
        if demodl == -1:
            demodl = nowsec+25
            print("*** Next input in less than 25s ***")
        elif nowsec >= demodl:
            resultk = ""
            resultv = 0
            for k in demoinputs.keys():
                if demoinputs[k] > resultv:
                    resultk = k
                    resultv = demoinputs[k]
            if resultv == 0:
                print("Input: N/A")
            else:
                print("*** Input:",resultk,"with",resultv,"votes ***")
            demoinputs.clear()
            demodl += 25
            tenscntdwn = 0
            print("*** Next input in less than 25s ***")
        elif demodl-nowsec <= 10 and tenscntdwn == 0:
            print("*** Next input in less than 10s ***")
            tenscntdwn = 1

    try:
        stream = twitchs.recv(1024).decode("UTF-8")
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
            if user == "Boy69162000" and commRE != None:
                if mode != msg[1:]:
                    print("*** Mode switched to", msg[2:],"***")
                    mode = msg[2:]
                    if mode == "democracy":
                        nowsec = time.time()
                        demodl = nowsec+25
                        tenscntdwn = 0
                        print("*** Next input in less than 25s ***")
            elif mode == "anarchy" and anarRE != None:
                inputs = msg[1:]
                print("{:>25} {}".format(user,inputs))
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
                print("{:>25} {}".format(user,inputs))
