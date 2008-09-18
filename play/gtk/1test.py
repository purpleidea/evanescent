#!/usr/bin/python

import os
import gtk
import pygtk
import gobject
import pynotify
import threading

pygtk.require('2.0')
# initialize the gtk thread engine
gtk.gdk.threads_init()


class pygtkmsg:

	def __init__(self, icon, tooltip=None):
		# todo validate icon path, look in dlls, and etc...
		self.icon = icon
		self.tooltip = tooltip

		self.gtk = {}		# keep the namespace clean and store all the gtk objects in a big dictionary

		# icon for tray
		self.gtk['icon'] = gtk.StatusIcon()
		self.gtk['icon'].set_from_file(os.path.join(os.getcwd(), self.icon))

		# on click for icon signal
		#self.gtk['icon'].connect("activate", icon_clicked)

		if not pynotify.init(__file__):
			raise ImportError('can\'t initialize pynotify')


	def msg(self, title, msg, icon=None, secs=10):


		if icon is not None and os.path.exists(icon):
			# image uri
			uri = 'file://' + os.path.abspath(os.path.curdir) + icon
			n = pynotify.Notification(title, msg, uri)
		else:
			n = pynotify.Notification(title, msg)

		if type(secs) is int: n.set_timeout(abs(secs)*1000)

		#n.set_hint("x", x)
		#n.set_hint("y", y)
		#n.attach_to_widget(?)
		# FIXME: appears in the wrong place
		n.attach_to_status_icon(self.gtk['icon'])
		if not n.show():
			return False

		return True


temp = pygtkmsg('favicon.ico')
#temp.go()
temp.msg('hey', 'there')

import time
time.sleep(2)


import sys
sys.exit(0)

"""
width = 728
height = 358
win = gtk.Window()
win.set_property('deletable', False)
win.set_property('skip-taskbar-hint', False)
win.set_geometry_hints(gtkmoz,width,height)
win.set_resizable(False)
win.add(gtkmoz)
win.show()
"""

menu = gtk.Menu()
quit = gtk.MenuItem("click here to quit...")
quit.connect("activate", gtk.main_quit)
quit.show()
menu.append(quit)


(screen, rectangle, orientation) = icon.get_geometry()
x = rectangle.x
y = rectangle.y
print rectangle.width
print rectangle.height
# TODO: calculate the centre of the rectangle...
print x
print y


gobject.timeout_add(3000, do_timer, count)

print 'running gtk.main()'
gtk.main()

print 'done'

