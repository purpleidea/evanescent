#!/usr/bin/python
"""
    Evanescent machine idle detection and shutdown tool.
    Copyright (C) 2008  James Shubin, McGill University
    Written for McGill University by James Shubin <purpleidea@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""this is the evanescent client that runs in the machines session"""

import os		# for path manipulations
import datetime		# for time delta calculations
import math		# for math.ceil

# frontend, gui related
import gtk		# for status icon
import pynotify		# for notifications

import gobject		# for timeout_add, etc...

# backend, evanescent related
import idle.idle as idle
import evanescent.config as config
import evanescent.exclusions as exclusions

class eva:

	def __init__(self, icon='favicon.ico'):
		"""constructor for the eva class."""

		# LOOP ########################################################
		self.warned = False	# warned datetime value

		# GOBJECT #####################################################
		# timer id
		self.source_id = None

		# GTK #########################################################
		self.icon = gtk.StatusIcon()
		self.icon.set_from_file(str(icon))

		self.menu = gtk.Menu()

		# TODO: do we want a menu? and what would it do?
		quit = gtk.MenuItem("Quit")
		quit.connect("activate", gtk.main_quit)
		quit.show()
		self.menu.append(quit)

		self.icon.connect("activate", self.icon_clicked)
		self.icon.connect("popup-menu", self.show_menu)

		# PYNOTIFY ####################################################

		# build a uri
		uri = "file://" + os.path.join(os.path.abspath(os.getcwd()), icon)
		#if self.DEBUG: debug('icon uri: %s' % uri)

		# make a dummy notification but never show() it. this is so that
		# we can just use the n.update() function to replace messages.
		self.n = pynotify.Notification(' ', '', uri)

		# FIXME: what does this do ?
		#n.set_category("device")

		# set the urgency
		#n.set_urgency(pynotify.URGENCY_LOW)
		n.set_urgency(pynotify.URGENCY_NORMAL)
		#n.set_urgency(pynotify.URGENCY_CRITICAL)

		# position the notification so that it points to the `tray' icon
		self.n.attach_to_status_icon(self.icon)

		# add some relevant buttons
		# TODO: decide on which ones to use if any
		self.n.add_action("default", "Default Action", self.default_cb)
		self.n.add_action("help", "Help", self.help_cb)
		self.n.add_action("logout", "Logout", self.logout_cb)
		self.n.add_action("postpone", "Postpone", self.postpone_cb)

		# self destruct message in x milliseconds
		#self.n.set_timeout(pynotify.EXPIRES_NEVER)
		#self.n.set_timeout(10*1000)




		"""
		#n.connect('closed', self.handle_closed) # run some code when closed signal gets called??????
		#def handle_closed(self,n):
		#	n.close()
		#	gtk.main_quit()

		if not n.show():
			print "Failed to send notification"

		# we can do this to update an existing pynotification
		#n.update("New Summary", "New Message")
		#n.show() ...
		"""


	# WORKING LOOP ########################################################
	def loop(self):
		"""internal main loop that checks for is idle() ? and etc..."""

		sleep = config.SLEEPTIME	# sleep time in seconds

		e = exclusions.exclusions(yamlconf=config.THECONFIG)
		# do the check, and it it passes get the good value.
		result = e.is_fileok()
		if result: result = e.is_excluded()
		# otherwise it's false anyways! not excluded!
		else: pass # TODO: write DEBUG MSG('file format bad.')

		if not result:

			if idle.is_idle(config.IDLELIMIT):

				if self.warned:

					# how long have we been warned for ?
					timedelta = datetime.datetime.today() - self.warned
					delta = int(math.ceil(timedelta.seconds + (timedelta.days*24*60*60) + (timedelta.microseconds*(1/1000000))))
					# if warning time is up!
					if delta > config.COUNTDOWN:

						#TODO: DO_LOGOFF()
						return False

					else:
						sleep = delta+1

				# do warn
				else:
					self.warned = datetime.datetime.today()
					# TODO: SHOW_WARNING_MESSAGE

					# sleep less often (to see if someone
					# taps a mouse) but make sure that we
					# wake up in time before countdown is up
					sleep = min(config.COUNTDOWN, config.FASTSLEEP)


			# not idle
			else:
				if self.warned:
					#self.logs['dialog'].info('log off canceled, not idle anymore.')
					# TODO: SHOW_NOT_IDLE_ANYMORE_MESSAGE
					self.warned = False

				sleep = config.SLEEPTIME

		# is excluded
		else:
			if self.warned:
				#self.logs['dialog'].info('log off canceled, you\'re currently excluded.')
				# TODO: SHOW_CURRENTLY_EXCLUDED_MESSAGE
				self.warned = False

			sleep = config.SLEEPTIME

		e = None	# clean up the object

		# remove the timeout, and reschedule an event when necessary
		gobject.source_remove(self.source_id)

		# add a new timeout so this gets called again
		# FIXME: choose a good time delay in ms
		self.source_id = gobject.timeout_add(sleep*1000, self.loop)

	# MAIN ################################################################
	def main(self):
		"""main to run for the class."""

		# make the notify work
		if not pynotify.init('eva'):
			# FIXME: fall back to a different messaging alternative.
			sys.exit(1)

		# FIXME: choose a good time delay in ms
		self.source_id = gobject.timeout_add(1000, self.loop)

		# run the main loop
		gtk.main()


	# HANDLERS ############################################################
	def show_menu(self, icon, button, time):
		"""handler for status icon right click"""
		# TODO: check the below line of code is correct
		self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.icon)


	def icon_clicked(self, icon, event=None):
		"""handler for status icon left click"""
		if self.win.get_property('visible'):
			self.win.hide()
		else:
			self.win.present()






if __name__ == '__main__':
	evaobj = eva()
	evaobj.main()


"""



import pygtk	# for pynotify cb actions?
pygtk.require('2.0')



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
"""
