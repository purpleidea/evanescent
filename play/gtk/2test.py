#!/usr/bin/python
import threading
import time
import gtk

gtk.gdk.threads_init()

class MessageSetter(threading.Thread):
	"""this class sends out the pynotify message."""


	def __init__(self, label):

		# override the __init__() of the inherited class
		# but still call the original init that we need.
		super(MessageSetter, self).__init__()
		self.label = label


	# thread event, stops the thread if it is set
	stopthread = threading.Event()

	def run(self):
		"""run method, this is the code that runs while thread is alive."""
		
		# while the stopthread event isn't set, the thread keeps going on
		while not(self.stopthread.isSet()):
			# acquire the gtk global mutex
			gtk.gdk.threads_enter()

			# do something
			print self.label

			# release the gtk global mutex
			gtk.gdk.threads_leave()

			# thread now sleeps
			time.sleep(1)

	def stop(self):
		"""stop method, sets the event to terminate the thread's main loop"""
		self.stopthread.set()


def main_quit(threads):
	"""main_quit function, it stops the thread and the gtk's main loop"""

	for x in threads:
		x.stop()

	gtk.main_quit()

#Connecting the 'destroy' event to the main_quit function
#window.connect('destroy', main_quit)

#Creating and starting the thread
ms = MessageSetter('label1')
ms.start()
time.sleep(0.5)
ms2 = MessageSetter('label2')
ms2.start()


import gobject
gobject.timeout_add(5000, main_quit, [ms, ms2])

gtk.main()

