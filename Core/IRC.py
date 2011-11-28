import socket, threading, random, time
from Events import *
from Functions import *
from Log import *
import json



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
        
        self.connected = False

        self.nick = "LOIC2_" + randomString(8)
        self.ops = []
        #log( "Nick:"+ self.nick)

        getEventManager().addListener(IRC_RECV, self.parseIRCString)


    def connect(self):
        if self.host.endswith('.onion'):
            event = Event(IRC_EVENT,"Using Tor")
            getEventManager().signalEvent(event)
            import socks
            self.socket.settimeout(30)
            self.socket = socks.socksocket(_sock=self.socket)
            self.socket.setproxy(proxytype=socks.PROXY_TYPE_SOCKS5,addr='127.0.0.1',port=9050)
        event = Event(IRC_EVENT,"Connecting...")
        getEventManager().signalEvent(event)
        self.listenThread = ListenThread(self.socket, self)

        try:
            self.socket.connect((self.host, self.port))
        except Exception as e:
            event = EVent(IRC_EVENT, "Connection Failure, "+str(e) )
            getEVentManager().signalEvent(event)
            return
        
        if self.online_hook:
            self.online_hook()

        self.connected = True

        self.listenThread.start()
        self.socket.send("NICK %s\r\n" % self.nick)
        self.socket.send("USER IRCLOIC %s blah :Newfag's remote LOIC\r\n" % self.host)

    def changeChannel(self, newchannel):
        self.send("PART %s\r\n" % self.channel)
        self.send("JOIN %s\r\n" % newchannel)
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
            self.send("PONG " + string[5:] + "\r\n")
        elif string[0] == ":":
            info = string.split(" ")
            if info[1] in [ "TOPIC","332"] and info[2] == self.channel:
                t = info[3:]
                t[0] = t[0][1:]
                topic = ''
                for s in t:
                    topic += s + ' '
                try:
                    target = json.loads(topic)
                    event = Event(GOT_TARGET,target)
                    getEventManager().signalEvent(event)
                except:
                    event = Event(ERR,'Hivemind Version May be Incompatible')
                    getEventManager().signalEvent(event)
            if info[1] == "MODE" and info[2] == self.channel:
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
                event = Event(IRC_EVENT,"Connection Established")
                getEventManager().signalEvent(event)
                
            elif info[1] == "002":
                self.send("JOIN %s\r\n" % self.channel)
        else:
            event = Event(ERR,"%s ! Reconnecting..."%string)
            getEventManager().signalEvent(event)
            self.disconnect()

            event = Event(IRC_RESTART, None)
            getEventManager().signalEvent(event)

    def stop(self):
        if self.listenThread:
            self.listenThread.stop()
        

    def send(self,data):
        try:
            self.socket.send(data)
        except Exception as e:
            getEventManager().signalEvent(Event(ERR,"Connection Failure: %s"%e))
