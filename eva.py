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
# TODO: add _() for gettext

import os					# for path manipulations
import sys					# for sys.exit
import datetime					# for time delta calculations
import math					# for math.ceil

import gtk					# for status icon
import pynotify					# for notifications
import gobject					# for timeout_add, etc...
import dbus					# for message passing
import dbus.mainloop.glib

import evanescent.idle.idle as idle		# idle package
import evanescent.logout.logout as logout	# logout package
import evanescent.config as config		# config module
import evanescent.exclusions as exclusions	# exclusions module
import evanescent.misc as misc			# misc functions module
import evanescent.edbus as edbus		# evanescent dbus classes

import logginghelp				# my wrapper for logging


class eva:

	# CONSTRUCTOR #########################################################
	def __init__(self):
		"""constructor for the eva class."""

		# MISC ########################################################
		self.name = 'eva'		# for use as a name identifier

		self.warned = False		# warned datetime value
		self.delta = 0			# time delta for warn

		# icon pixbuf
		self.iconfile = os.path.join(config.SHAREDDIR, 'evanescent.png')
		#self.pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.iconfile, width?, height?)
		self.pixbuf = gtk.gdk.pixbuf_new_from_file(self.iconfile)

		# LOGGING #####################################################
		obj = logginghelp.logginghelp(name=self.name, wordymode=config.WORDYMODE,
		mylogpath=[config.MYLOGPATH, os.path.join(misc.get_home(), '.eva.log')],
		logserver=config.LOGSERVER, logformat=config.LOGFORMAT)

		self.log = obj.get_log()	# main logger

		# GOBJECT #####################################################
		self.source_id = None		# timer id

		# DBUS ########################################################
		self.session_bus = None		# dbus system bus handle

		# GTK #########################################################
		# about dialog
		self.about = None
		gtk.about_dialog_set_url_hook(self.show_uri)

		# icon
		self.icon_source_id = None		# source id for callback
		self.icon = gtk.StatusIcon()
		self.icon.set_from_pixbuf(self.pixbuf)
		self.icon_visibility(False)		# hide it

		# build a menu
		self.menu = gtk.Menu()

		# menu:help
		help = gtk.ImageMenuItem(gtk.STOCK_HELP)
		help.connect('activate', self.help_activate)
		help.show()
		self.menu.append(help)

		# menu:about
		about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		about.connect('activate', self.about_activate)
		about.show()
		self.menu.append(about)

		# menu:quit
		quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		quit.connect('activate', self.main_quit)
		quit.show()
		self.menu.append(quit)

		# TODO: should we have something happen? maybe an info bubble?
		#self.icon.connect('activate', self.icon_activate)	# left
		self.icon.connect('popup-menu', self.icon_popupmenu)	# right

		# PYNOTIFY ####################################################

		self.pynotify = True	# is pynotify active? assume yes for now

		# try to turn on pynotify
		if not pynotify.init(self.name):
			# fall back to a different messaging alternative.
			self.pynotify = False	# disable pynotify
			misc.console_msg('the main notifications system is not available. notifications will be sent to the console.')

		# make a dummy notification but never show() it. this is so that
		# we can easily use the n.update() function to replace messages.
		self.n = pynotify.Notification(' ', '')

		# set the icon
		self.n.set_icon_from_pixbuf(self.pixbuf)

		# position the notification so that it points to the `tray' icon
		self.n.attach_to_status_icon(self.icon)

		# self destruct message in x milliseconds
		self.n.set_timeout(pynotify.EXPIRES_NEVER)
		#self.n.set_timeout(10*1000)

		# signal handle for notification closed
		self.n.connect('closed', self.notification_closed)

		#self.n.set_category("device")	# what does this do ?
		# from: libnotify/notification.c: Sets the category of this
		# notification. This can be used by the notification server to
		# filter or display the data in a certain way.

		# set the default urgency
		self.n.set_urgency(pynotify.URGENCY_NORMAL)

		# add some relevant buttons
		# TODO: decide on which ones to use if any
		#self.n.add_action("default", "Default Action", self.notification_default)
		#self.n.add_action("help", "Help", self.notification_help)
		#self.n.add_action("logout", "Logout", self.notification_logout)
		#self.n.add_action("postpone", "Postpone", self.notification_postpone)


	# HANDLERS ############################################################
	def notification_closed(self, n=None, now=False):
		"""handler for pynotify dialog closed."""
		# TODO: in example code, i've seen others execute the close()
		# method of the dialog, on the closed event handler. don't know
		# if this makes any sense to do, but it doesn't seem to hurt at
		# the moment. maybe someone can comment and suggest any changes
		# or reasoning for this code. too bad the docs suck!
		if n is None: n = self.n	# defaults, so anyone can call
		self.icon.set_blinking(False)	# stop the blinking if any.
		self.n.close()
		# hide the tray icon now, or in say 15 seconds
		if bool(now): self.icon_visibility(0, False)
		else: self.icon_visibility(15, False)


	def help_activate(self, widget):
		"""show the help info."""
		# TODO: run better help in the future
		self.log.debug('showing help')
		self.show_uri(self.menu, 'http://www.cs.mcgill.ca/~james/help/eva/')


	def about_activate(self, widget):
		"""show an about dialog."""
		if self.about is not None:
			self.about.present()	# show the user where it is
			return False	# don't make another dialog below.

		self.about = gtk.AboutDialog()
		self.about.set_program_name(self.name)
		version = misc.get_version(config.SHAREDDIR)
		if version is not None: self.about.set_version(version)
		authors = misc.get_authors(config.SHAREDDIR)
		if len(authors) > 0: self.about.set_authors(authors)
		license = misc.get_license(config.SHAREDDIR)
		if license is not None: self.about.set_license(license)
		year = datetime.datetime.now().year
		# TODO: add real copyright symbol
		copyright = \
		'Copyright (c) 2008-%d James Shubin, McGill University' % year
		self.about.set_copyright(copyright)
		self.about.set_comments('Evanescent/Eva machine idle detection and shutdown tool (server/client)')
		self.about.set_website('http://www.cs.mcgill.ca/~james/code/')
		self.about.set_website_label('Evanescent Website')
		self.about.set_logo(self.pixbuf)
		# TODO: remove this line when our icon isn't so ugly
		self.about.set_logo(gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(config.SHAREDDIR, 'evanescent.svg'), 32, 32))
		self.about.run()
		# TODO: is the below statement correct? i think it is. NEEDSINFO
		# turns out if you call about.destroy from somewhere else, then
		# somehow it causes the about.run() function to unwait and move
		# on down and finish the execution here. the result is that the
		# main quit handler that i made can cause the open about dialog
		# to close and let the whole program close gracefully. i think!
		self.about.destroy()
		self.about = None


	def show_uri(self, dialog, link):
		"""open a uri."""
		# TODO: according to the docs at:
		# http://www.pygtk.org/docs/pygtk/class-gtkmountoperation.html#function-gtk--show-uri
		# the constant: gtk.gdk.CURRENT_TIME should exist but doesn't.
		# find out how to get it and put it in the function below. maybe
		# the latest version of pygtk will fix this. we should also be
		# able to remove self.about.get_screen() and replace with: None.
		self.log.debug('showing uri: %s' % link)
		gtk.show_uri(dialog.get_screen(), link, 0)


	def icon_popupmenu(self, icon, button, time):
		"""handler for status icon right click"""
		self.icon_visibility(60)	# reschedule icon to hide in 60
		# old style below:
		#self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.icon)
		self.menu.popup(None, None, None, button, time)


	def icon_activate(self, icon, event=None):
		"""handler for status icon left click"""
		if self.win.get_property('visible'):
			self.win.hide()
		else:
			self.win.present()


	def main_quit(self, obj=None):
		"""make my own quit signal handler."""
		# TODO: if there is a better way to do this, someone tell me!
		self.log.debug('running quit')
		self.notification_closed(now=True)	# close any leftovers
		if self.about is not None: self.about.destroy()
		gtk.main_quit()


	# MESSAGING ###########################################################
	def msg(self, message, title=None, urgency=None, timeout=None, WORKAROUND=True, WORKAROUND2=True):
		"""more general message wrapper around `write' and pynotify."""

		# TODO: workaround for attach_to_status_icon placement bug
		# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=456610
		if self.pynotify and WORKAROUND:
			# Why does this work? because we need to let control go
			# back into the gtk main loop, and hang out a little bit
			# so that the position data from icon.set_visible() gets
			# updated (presumably) so that subsequent calls to the
			# attach_to_status_icon() function get better placement
			# data. :(
			self.icon_visibility(True)		# show this now!
			gobject.timeout_add(1000, self.msg, message, title, urgency, timeout, False)
			return

		# initial checks, plus fix pynotify name conventions and reqs.
		assert type(message) is str		# we need at least one string

		# if there is no title, we need at least one char in message
		if title is None:
			if len(message) == 0:
				self.log.error('can\'t send an empty message.')
				return

			# and do switch
			title = message
			message = None

		elif type(title) is str:
			if len(title) == 0:
				self.log.error('can\'t send an empty message.')
				return

		# if pynotify is off
		if not self.pynotify:
			# fall back to sending a console message
			if message is None: misc.console_msg('%s' % title)
			else: misc.console_msg('%s: %s' % (title, message))
			return

		# TODO: workaround for libnotify resize bug
		# if we update a message with lots of text, with one that has
		# very little text, the dialog doesn't shrink and the user sees
		# one that is mostly empy, taking up lots of space. if we close
		# the old one just before we re-open it, then the size gets
		# adjusted and we don't see the visual glitch! :P
		if WORKAROUND2: self.n.close()

		# remove the icon get hidden timeout
		self.icon_visibility(None)

		# make the message
		self.n.update(title, message)

		# set the urgency
		if urgency in [pynotify.URGENCY_LOW, pynotify.URGENCY_NORMAL, pynotify.URGENCY_CRITICAL]:
			self.n.set_urgency(urgency)

		# set the timeout
		if timeout is True: self.n.set_timeout(pynotify.EXPIRES_DEFAULT)
		elif timeout is None: self.n.set_timeout(pynotify.EXPIRES_NEVER)
		elif type(timeout) is int: self.n.set_timeout(timeout)

		self.icon_visibility(True)	# show the tray icon

		if self.n.show():		# this fails if icon not visible

			# TODO: find a way to *read* urgency from self.n eg:
			# something like get_urgency() and if it is CRITICAL
			# then do the blinking. otherwise don't. for now we
			# can work around this by assuming it is set in this
			# msg(urgency=<URGENCY>) function call here.
			if urgency == pynotify.URGENCY_CRITICAL:
				# make the icon blink, in case it wasn't already
				self.icon.set_blinking(True)
			else:
				# or turn it off in case it was on
				self.icon.set_blinking(False)

		else:
			# hide the tray icon if the notification fails
			self.icon_visibility(False)
			self.log.error('pynotify failed to send a message.')

			# fall back to sending a console message
			if message is None: misc.console_msg('%s' % title)
			else: misc.console_msg('%s: %s' % (title, message))

		# TODO: workaround needed for broken libnotify/pynotify
		if WORKAROUND: return False


	# MISCELLANEOUS ########################################################

	def welcome_info(self):
		"""send a notification to the user that informs them that they
		could get logged off if idle. check in their $HOME/.evanescent
		to see if they have chosen to ignore this warning."""
		home = misc.get_home()
		self.log.debug('user\'s home directory is: %s' % str(home))

		# TODO: add an option that if true, *always* welcomes the user.
		# useful for people who like to remember that eva is running (also good for debugging)
		filename = os.path.join(home, '.eva.conf.yaml')
		defaults = {'WELCOMEME': True}
		expected = {'WELCOMEME': bool}
		conf = config.config(
			filename=filename, defaults=defaults, expected=expected
		)
		data = conf.run(make=False)

		if data['WELCOMEME']:
			self.msg(title='welcome to eva', message='eva is a ' \
			'client program that notifies you when your session ' \
			'is idle. it can automatically log you out, lock your '\
			'screen or perform some custom action like pausing '\
			'your music.' + (2 * os.linesep) + 'once you dismiss '\
			'this message, it won\'t pop up to bother you anymore.',
			urgency=pynotify.URGENCY_NORMAL,
			timeout=pynotify.EXPIRES_NEVER)

			# turn off future welcome messages
			data['WELCOMEME'] = False
			conf.store(data)
		else:
			self.log.debug('skipping welcome message')


	def icon_visibility(self, seconds=0, visibility=False):
		"""set the icon visibility. this helper function automatically
		schedules the timing for the set_visible call. if you call this
		with just one parameter: None, then it cancels the timeout. if
		you call it with one parameter: a bool, then it sets that
		visibility right now. and if you call it with two parameters:
		seconds, and visibility, then it sets a timeout to set the
		requested visibility in that many seconds. 0 seconds means now.
		anytime you run the function it will clear any existing timeout
		and it might add a new one."""
		# remove any pending icon: `set_visible' timeouts
		if type(self.icon_source_id) is int:
			gobject.source_remove(self.icon_source_id)
			self.icon_source_id = None

		# if the function is called with just a bool, then set that
		# right away.
		if type(seconds) is bool:
			visibility = seconds
			seconds = 0

		# do it now
		if seconds == 0: self.icon.set_visible(visibility)
		elif seconds > 0:
			# schedule a new one
			self.icon_source_id = \
			gobject.timeout_add(seconds*1000, self.icon.set_visible, visibility)


	# WORKING LOOP ########################################################
	def loop(self):
		"""main loop for eva that runs the business logic, etc..."""

		self.log.debug('entering local loop()')
		sleep = idle.timeleft(config.IDLELIMIT)	# sleep time in seconds

		e = exclusions.exclusions(yamlconf=config.THECONFIG)
		# do the check, and if it passes get the good value.
		result = e.is_fileok()
		if result: result = e.is_excluded()
		# otherwise it's false anyways! not excluded!
		else:
			self.log.warn('problem with config file.')
			self.log.warn('assuming no exclusions.')

		e = None			# clean up the object

		# if not excluded
		if not result:
			self.log.warn('you are currently NOT excluded from idle-logout.')

			if idle.is_idle(config.IDLELIMIT):

				self.log.info('user is currently idle.')
				if self.warned:

					# how long have we been warned for ?
					timedelta = datetime.datetime.today() - self.warned
					self.delta = int(math.ceil(timedelta.seconds + (timedelta.days*24*60*60) + (timedelta.microseconds*(1/1000000))))
					timeleft = config.COUNTDOWN - self.delta
					# if warning time is up!
					if self.delta > config.COUNTDOWN:

						self.log.fatal('you are being logged off due to inactivity.')
						self.msg(title='you are currently idle',
						message='you are being logged off due to inactivity',
						urgency=pynotify.URGENCY_CRITICAL,
						timeout=pynotify.EXPIRES_NEVER)
						# do the actual logout
						logout.logout()
						return False

					else:
						# update the timeleft message
						# or not depending on option.
						if config.UPDATEMSG:
							# update the message
							self.msg(title='You are currently idle',
							message='your session will be logged off in about %d seconds (and counting) if you continue to be idle.' % (timeleft) + os.linesep + 'press a key or move your mouse to cancel the impending logout.',
							urgency=pynotify.URGENCY_CRITICAL,
							timeout=pynotify.EXPIRES_NEVER)

						sleep = min(timeleft, config.FASTSLEEP)

				# do warn
				else:
					self.warned = datetime.datetime.today()
					self.log.warn('you are currently idle. rectify this or your session will be automatically logged off.')
					self.msg(title='You are currently idle',
					message='your session will be logged off in about %d seconds (and counting) if you continue to be idle.' % (config.COUNTDOWN) + os.linesep + 'press a key or move your mouse to cancel the impending logout.',
					urgency=pynotify.URGENCY_CRITICAL,
					timeout=pynotify.EXPIRES_NEVER)

					# TODO: play a sound or some sort of
					# audio notification like voice or beep

					# sleep less often (to see if someone
					# taps a mouse) but make sure that we
					# wake up in time before countdown is up
					# a faster sleep updates the countdown
					# counter faster, but wastes more cpu.
					sleep = min(config.COUNTDOWN, config.FASTSLEEP)

			# not idle
			else:
				self.log.info('user is not idle.')
				if self.warned:
					self.log.info('log off canceled, not idle anymore.')
					self.msg(message='log off canceled, you\'re not idle anymore',
					title=None,
					urgency=pynotify.URGENCY_LOW,
					timeout=pynotify.EXPIRES_DEFAULT)
					self.warned = False

				sleep = idle.timeleft(config.IDLELIMIT)

		# is excluded
		else:
			self.log.info('you are currently excluded from idle-logout.')
			if self.warned:
				self.log.info('log off canceled, you\'ve just been excluded.')
				self.msg(message='log off canceled, you\'ve just been excluded.',
				title=None,
				urgency=pynotify.URGENCY_LOW,
				timeout=pynotify.EXPIRES_DEFAULT)
				self.warned = False

			#sleep = config.SLEEPTIME	# CHANGED IN FAVOUR OF:
			sleep = max(idle.timeleft(config.IDLELIMIT), self.get_exclusions_changed_time())

		sleep = max(1, sleep)		# sleep for at least one second
		self.log.info('going to sleep for %d seconds.' % sleep)

		# add a new timeout so this gets called again
		self.source_id = gobject.timeout_add(sleep*1000, self.loop)

		# this loop ends, and we wait for the above rescheduled event
		return False


	def get_exclusions_changed_time(self):
		# TODO: make this ideally check the next time the exclusions are
		# liable to include the user (by parsing and looking at date/time
		# if possible. if this is too hard (which it could be) then sleep
		# for some constant amount of time shown below. also, add a watch
		# on the exclusions file, and if it changes, then wake up and see
		# if the exclusions are now enough to let someone get logged off!
		# TODO: the later part of this can maybe be done with pyinotify.
		# TODO: i could potentially consult an algorithmist to see if it
		# is worth it to write the former part of the above description.
		return config.SLEEPTIME


	# MAIN ################################################################
	def main(self):
		"""main to run for the class."""

		if config.DEBUGMODE: self.log.debug('debugmode: on')

		# should evanescent be disabled, and exit right away?
		if not(config.STARTMEUP):
			self.log.debug('shouldn\'t start, now exiting.')
			sys.exit()

		# TODO: attach a signal for mouse movement to some function
		# which updates the "your machine is idle" dialog whenever it
		# is called. i think this is possible because of this link:
		# http://library.gnome.org/devel/gobject/unstable/signal.html
		# UPDATE: actually it might not be possible because it relies
		# on the motion-notify-event of a gtkwidget object which we
		# won't have access to. (there is just the icon and pynotify)

		# make dbus happy
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

		self.session_bus = dbus.SessionBus()		# make the bus
		bus_name = dbus.service.BusName(edbus._service, bus=self.session_bus)

		edbus.Eva(self, bus_name, edbus._path)		# register dbus

		# run informational welcome message script.
		gobject.idle_add(self.welcome_info)

		# start off our initial event source in one second from now.
		self.source_id = gobject.timeout_add(1*1000, self.loop)

		# run the main loop
		gtk.main()


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

"""

