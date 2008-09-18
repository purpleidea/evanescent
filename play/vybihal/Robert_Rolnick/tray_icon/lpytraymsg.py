#!/usr/bin/python
import os
import gobject
import gtk
import pynotify

# Provides a tray icon for linux! However, displaying the icon (and notification) is a BLOCKING call.
# TODO: Look into threading this functionality, so it doesn't need to be blocking

class lpytraymsg:

	statusIcon = None
	notify = None

	def __init__(self):
		pass

	def create_tray(self, icon, title):
		pynotify.init("pynotify")
		self.statusIcon=gtk.status_icon_new_from_file((os.path.dirname(__file__) + "/windows/" + icon)) #TODO: Is there a more elegant way of doing this?

		##No need for a pop-up menu, clicking kills the icon
		#menu = gtk.Menu()
		#menuItem = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		#menuItem.connect('activate', self.on_about)
		#menu.append(menuItem)
		#menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		#menuItem.connect('activate', self.on_quit, self.statusIcon)
		#menu.append(menuItem)


		self.statusIcon.set_visible(False)
		self.statusIcon.connect('activate', self.on_quit)
		self.statusIcon.set_blinking(True)
		#self.statusIcon.connect('popup-menu', self.on_menu, menu)
		self.statusIcon.set_tooltip(title)

	def msg(self, title, text):
		self.statusIcon.set_visible(True)
		self.notify = pynotify.Notification(title,text,"pynotify")
		self.notify.set_urgency(pynotify.URGENCY_NORMAL)
		self.notify.attach_to_status_icon(self.statusIcon)
		self.notify.set_timeout(pynotify.EXPIRES_NEVER) #TODO: Read this from config
		self.notify.connect('closed', self.handle_closed)
		gobject.timeout_add (500, self.show_notification)   #required for  notification to line up with icon (need a short delay for the icon to become visible first.)
		gtk.main() #gtk only renders graphics when this BLOCKING call is made. Clicking on the notification icon OR bubble unblocks you.

	def show_notification(self):
		self.notify.show()

	def on_quit(self, widget, data = None):
		self.notify.close()

	def handle_closed(self, n):
		self.statusIcon.set_visible(False)
		gtk.main_quit()

	def on_menu(self, widget, button, time, data = None): #Menu is not currently in use, but would be right click menu on icon
	    if button == 3:
		if data:
		    data.show_all()
		    data.popup(None, None, None, 3, time)
	    pass


	def on_about(self, widget, data = None): #Not currently in use, but it is the aboutDialog from the menu.
		aboutDialog = gtk.AboutDialog()
		aboutDialog.set_name('evanescent')
		aboutDialog.set_version('56')
		aboutDialog.set_license("""GNU AFFERO GENERAL PUBLIC LICENSE
VERSION 3.0""")
		aboutDialog.run()
		aboutDialog.destroy()
