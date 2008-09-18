#!/bin/sh
"""echo"
# dirty hack to set ld path
exec env LD_LIBRARY_PATH=/usr/lib/firefox python $0
"""

import gtk
import os

def icon_clicked(icon,event=None):
	if win.get_property('visible'):
		win.hide()
	else:
		win.present()

def show_menu(icon, button, time):
	menu.popup(None, None, gtk.status_icon_position_menu, button, time, icon)

try:
	os.mkdir('/tmp/gtk')
except:
	pass

icon = gtk.StatusIcon()
os.chdir("/tmp/gtk")
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

menu = gtk.Menu()
quit = gtk.MenuItem("Quit")
quit.connect("activate", gtk.main_quit)
quit.show()
menu.append(quit)
		
icon.connect("activate", icon_clicked)
icon.connect("popup-menu", show_menu)
gtk.main()
