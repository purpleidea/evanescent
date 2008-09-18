#!/usr/bin/python

#from dbus.mainloop.glib import DBusGMainLoop
#DBusGMainLoop(set_as_default=True)

import pygtk	# for pynotify cb actions?
pygtk.require('2.0')

import gtk

import pynotify	# for pynotify
import os
import gobject	# extra for watcher


### FUNCTIONS ###
def icon_clicked(icon,event=None):
	"""on icon left click"""
	if win.get_property('visible'):
		win.hide()
	else:
		win.present()


def show_menu(icon, button, time):
	"""on icon right click"""
	menu.popup(None, None, gtk.status_icon_position_menu, button, time, icon)


def wow_cb(n, action):
	#assert action == "wow"
	print "You clicked WOW"
	n.close()
	gtk.main_quit()

def help_cb(n, action):
	assert action == "help"
	print "You clicked Help"
	n.close()
	gtk.main_quit()

def default_cb(n, action):
	assert action == "default"
	print "You clicked the default action"
	n.close()
	gtk.main_quit()



def watcher(one, two, iconobj):
	"""watcher function"""
	print 'bing: %s' % two[0]
	two[0] = two[0] + 1
	if two[0] % 10 == 0:
		print 'one: %s, two: %s' % (one, str(two[0]))

		uri = "file://" + os.path.abspath(os.path.curdir) + "/favicon.ico"
		print "Sending " + uri

		n = pynotify.Notification("Summary", "message: %s; number: %d" % (one, two[0]), uri)
		n.attach_to_status_icon(iconobj)
		n.set_urgency(pynotify.URGENCY_LOW)
		#n.set_urgency(pynotify.URGENCY_NORMAL)
		#n.set_urgency(pynotify.URGENCY_CRITICAL)

		#n.set_category("device") #????????????????????????
		n.add_action("default", "Default Action", default_cb)
		n.add_action("help", "Help", help_cb)
		n.add_action("wow", "This is WOW", wow_cb)
		#n.add_action("empty", "Empty Trash", empty_cb)
		#n.set_timeout(pynotify.EXPIRES_NEVER)
		#n.connect('closed', self.handle_closed) # run some code when closed signal gets called??????
		#def handle_closed(self,n):
		#	n.close()
		#	gtk.main_quit()

		n.set_timeout(10000) # 10 seconds	# self destruct message in 10 seconds

		if not n.show():
			print "Failed to send notification"

		# we can do this to update an existing pynotification
		#n.update("New Summary", "New Message")
		#n.show() ...

	# if we return False then it won't be called anymore.
	return True

# make the notify work
if not pynotify.init("something"):
	sys.exit(1)

try:
	os.mkdir('/tmp/gtk')
except:
	pass
os.chdir("/tmp/gtk")
icon = gtk.StatusIcon()
if not(os.path.exists('favicon.ico')): os.system('wget http://www.mcgill.ca/favicon.ico')
icon.set_from_file('favicon.ico')

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

# menu w/ a menu item
menu = gtk.Menu()
quit = gtk.MenuItem("Quit")
quit.connect("activate", gtk.main_quit)
quit.show()
menu.append(quit)

icon.connect("activate", icon_clicked)
icon.connect("popup-menu", show_menu)

# try to add idle watcher
start = 0
# if you enclose start in [] then it gets passed by ref... and we can increment!
source_id = gobject.timeout_add(1000, watcher, 'hello!', [start], icon)

gtk.main()

