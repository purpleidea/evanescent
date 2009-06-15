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

import os				# for path manipulations
import datetime				# for time delta calculations
import math				# for math.ceil
import logging, logging.handlers	# for syslog stuff

# frontend, gui related
import gtk				# for status icon
import pynotify				# for notifications

import gobject				# for timeout_add, etc...

# backend, evanescent related
import evanescent.idle.idle as idle
import evanescent.config as config
import evanescent.exclusions as exclusions

class eva:

	# CONSTRUCTOR #########################################################
	def __init__(self, iconimage=config.ICONIMAGE):
		"""constructor for the eva class."""

		# MISC ########################################################
		self.name = 'eva'		# for use as a name identifier
		self.warned = False		# warned datetime value
		self.delta = 0			# time delta for warn
		self.iconimage = str(iconimage)	# store iconimage

		# LOGGING #####################################################
		self.log = None			# main logger
		self.logh = {}			# log handles
		self.logs = {}			# other log handles

		# setup the logging handles
		self.logging()

		# GOBJECT #####################################################
		self.source_id = None		# timer id

		# GTK #########################################################
		# about dialog
		self.about = None
		gtk.about_dialog_set_url_hook(self.show_uri)

		# icon
		self.icon_set_visible_source_id = None	# source id for callback
		self.icon = gtk.StatusIcon()
		self.icon.set_visible(False)		# hide it
		self.icon.set_from_file(self.iconimage)

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

		self.icon.connect('activate', self.icon_activate)	# left
		self.icon.connect('popup-menu', self.icon_popupmenu)	# right

		# PYNOTIFY ####################################################

		# build a uri
		self.uri = "file://" + os.path.join(os.path.abspath(os.getcwd()), self.iconimage)
		self.log.debug('icon uri: %s' % self.uri)

		# make a dummy notification but never show() it. this is so that
		# we can easily use the n.update() function to replace messages.
		self.n = pynotify.Notification(' ', '', self.uri)

		# position the notification so that it points to the `tray' icon
		self.n.attach_to_status_icon(self.icon)

		# self destruct message in x milliseconds
		self.n.set_timeout(pynotify.EXPIRES_NEVER)
		#self.n.set_timeout(10*1000)

		# signal handle for notification closed
		self.n.connect('closed', self.notification_closed)

		# FIXME: what does this do ?
		#self.n.set_category("device")

		# set the urgency
		#self.n.set_urgency(pynotify.URGENCY_LOW)
		self.n.set_urgency(pynotify.URGENCY_NORMAL)
		#self.n.set_urgency(pynotify.URGENCY_CRITICAL)

		# add some relevant buttons
		# TODO: decide on which ones to use if any
		#self.n.add_action("default", "Default Action", self.notification_default)
		#self.n.add_action("help", "Help", self.notification_help)
		#self.n.add_action("logout", "Logout", self.notification_logout)
		#self.n.add_action("postpone", "Postpone", self.notification_postpone)

	# LOGGING #############################################################
	def logging(self):
		"""setup logging. this function doesn't return any value."""
		# error logging levels:
		#	* CRITICAL
		#	* FATAL
		#	* ERROR
		#	* WARN
		#	* INFO
		#	* DEBUG

		# have every log use this format
		formatter = logging.Formatter(config.LOGFORMAT)

		# name a log route & set a level
		self.log = logging.getLogger(self.name)
		if config.WORDYMODE: self.log.setLevel(logging.DEBUG)
		else: self.log.setLevel(logging.WARN)

		# handler for stderr
		self.logh['StreamHandler'] = logging.StreamHandler()
		self.logh['StreamHandler'].setFormatter(formatter)
		self.log.addHandler(self.logh['StreamHandler'])

		# handler for global logging server
		# TODO: find a way to change the facility to 'evanescent' or rather: the self.name variable
		self.logh['SysLogHandler'] = logging.handlers.SysLogHandler(config.LOGSERVER, logging.handlers.SysLogHandler.LOG_LOCAL7)
		self.logh['SysLogHandler'].setFormatter(formatter)
		self.log.addHandler(self.logh['SysLogHandler'])

		# handler for windows event log
		if os.name == 'nt':
			self.logh['NTEventLogHandler'] = logging.handlers.NTEventLogHandler(self.name)
			self.logh['NTEventLogHandler'].setFormatter(formatter)
			self.log.addHandler(self.logh['NTEventLogHandler'])

		# handler for local disk
		# NOTE: using access() to check if a user is authorized to e.g. open a file before actually
		# doing so using open() creates a security hole, because the user might exploit the short
		# time interval between checking and opening the file to manipulate it. try and catch instead.
		try:
			self.logh['RotatingFileHandler'] = logging.handlers.RotatingFileHandler(config.MYLOGPATH, maxBytes=1024*100, backupCount=9)
			self.logh['RotatingFileHandler'].setFormatter(formatter)
			self.log.addHandler(self.logh['RotatingFileHandler'])
		except IOError:
			# you probably don't have the file permissions to open the file.
			# are you root, or do you need to be?
			self.log.warn('unable to open `%s\' for use as a log file.' % config.MYLOGPATH)
			if self.logh.has_key('RotatingFileHandler'): del self.logh['RotatingFileHandler']

		# handlers in x propagate down to everyone (y) in the x.y tree
		#self.logs['evalog'] = logging.getLogger('%s.evalog' % self.name)
		#self.logs['OTHERL'] = logging.getLogger('%s.OTHERL' % self.name)

		# send a hello message
		self.log.debug('hello from %s' % self.name)


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
		if bool(now): self.icon.set_visible(False)
		else:
			self.icon_set_visible_source_id = \
			gobject.timeout_add(15*1000, self.icon.set_visible, False)


	def help_activate(self, widget):
		"""show the help info."""
		# TODO: decide what to do here
		self.log.debug('FIXME: show help')


	def about_activate(self, widget):
		"""show an about dialog."""
		# TODO: customize this more

		if self.about is not None:
			self.about.present()	# show the user where it is
			return False	# don't make another dialog below.

		self.about = gtk.AboutDialog()
		self.about.set_program_name(self.name)
		self.about.set_version('0.1')	# TODO: change this dynamically.
		if len(self.get_authors()) > 0:
			self.about.set_authors(self.get_authors())
		if self.get_license() is not None:
			self.about.set_license(self.get_license())
		self.about.set_copyright('(c) James Shubin, McGill University')
		self.about.set_comments('Evanescent/Eva machine idle detection and shutdown tool (server/client)')
		self.about.set_website('http://www.cs.mcgill.ca/~james/code/')
		self.about.set_website_label('http://www.cs.mcgill.ca/~james/code/')
		# TODO: make icon bigger!
		self.about.set_logo(gtk.gdk.pixbuf_new_from_file(self.iconimage))
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
		# FIXME: according to the docs at:
		# http://www.pygtk.org/docs/pygtk/class-gtkmountoperation.html#function-gtk--show-uri
		# the constant: gtk.gdk.CURRENT_TIME should exist but doesn't.
		# find out how to get it and put it in the function below. maybe
		# the latest version of pygtk will fix this. we should also be
		# able to remove self.about.get_screen() with `None'.
		self.log.debug('showing uri')
		gtk.show_uri(self.about.get_screen(), link, 0)


	def icon_popupmenu(self, icon, button, time):
		"""handler for status icon right click"""
		# old style below:
		#self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.icon)
		self.menu.popup(None, None, None, button, time)


	def icon_activate(self, icon, event=None):
		"""handler for status icon left click"""
		if self.win.get_property('visible'):
			self.win.hide()
		else:
			self.win.present()


	def main_quit(self, obj):
		"""make my own quit signal handler."""
		# TODO: if there is a better way to do this, someone tell me!
		self.log.debug('running quit')
		self.notification_closed(now=True)	# close any leftovers
		#if self.about is not None: self.about.destroy()
		gtk.main_quit()


	# MESSAGING ###########################################################

	def msg(self, message, title=None, urgency=None, timeout=None, WORKAROUND=True, WORKAROUND2=True):
		"""more general message wrapper around `write' and pynotify."""

		# FIXME: workaround for attach_to_status_icon placement bug
		# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=456610
		if WORKAROUND:
			# Why does this work? because we need to let control go
			# back into the gtk main loop, and hang out a little bit
			# so that the position data from icon.set_visible() gets
			# updated (presumably) so that subsequent calls to the
			# attach_to_status_icon() function get better placement
			# data. :(
			self.icon.set_visible(True)	# show this now!
			gobject.timeout_add(1000, self.msg, message, title, urgency, timeout, False)
			return

		# initial checks, plus fix pynotify name conventions and reqs.
		assert type(message) is str		# we need at least one string

		# if there is no title, we need at least one char in message
		if title is None:
			if len(message) == 0:
				self.log.error('can\'t send an empty message.')

			# and do switch
			title = message
			message = None # OR '' ?
		elif type(title) is str:
			if len(title) == 0:
				self.log.error('can\'t send an empty message.')

		# FIXME: workaround for libnotify resize bug
		# if we update a message with lots of text, with one that has
		# very little text, the dialog doesn't shrink and the user sees
		# one that is mostly empy, taking up lots of space. if we close
		# the old one just before we re-open it, then the size gets
		# adjusted and we don't see the visual glitch! :P
		if WORKAROUND2: self.n.close()

		# remove the icon get hidden timeout
		if self.icon_set_visible_source_id is int:
			gobject.source_remove(self.icon_set_visible_source_id)
			self.icon_set_visible_source_id = None

		# make the message
		self.n.update(title, message, self.uri)

		# set the urgency
		if urgency in [pynotify.URGENCY_LOW, pynotify.URGENCY_NORMAL, pynotify.URGENCY_CRITICAL]:
			self.n.set_urgency(urgency)

		# set the timeout
		if timeout is True: self.n.set_timeout(pynotify.EXPIRES_DEFAULT)
		elif timeout is None: self.n.set_timeout(pynotify.EXPIRES_NEVER)
		elif type(timeout) is int: self.n.set_timeout(timeout)

		self.icon.set_visible(True)	# show the tray icon

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
			self.icon.set_visible(False)
			self.log.error('pynotify failed to send a message.')

		# TODO: send messages with a `write' module as well. (eg: os.system('write <message>'))
		# <write.send> ... ?

		# FIXME: workaround needed for broken libnotify/pynotify
		if WORKAROUND: return False

	# MISCELLANEOUS ########################################################

	def info(self):
		"""send a notification to the user that informs them that they
		could get logged off if idle. check in their $HOME/.evanescent
		to see if they have chosen to ignore this warning."""
		home = os.getenv('USERPROFILE', False) or os.getenv('HOME')
		self.log.debug('user\'s home directory is: %s' % str(home))

		"""
		if not; in $HOME/.evanescent: -> ignore=True
			self.msg(title='welcome to eva',
			message='This is a tool that...',
			urgency=pynotify.URGENCY_NORMAL,
			timeout=pynotify.EXPIRES_NEVER)
		"""
		# for now, always do this. HOWEVER:
		# FIXME this fast, because it's annoying
		self.msg(title='welcome to eva',
		message='this is a welcome message to inform the user about...',
		urgency=pynotify.URGENCY_NORMAL,
		timeout=pynotify.EXPIRES_NEVER)


	def get_authors(self):
		"""little function that pulls the authors from a text file."""
		try:
			f = open('AUTHORS', 'r')
			authors = f.readlines()
			# assume it's an author if there is an email
			return [ x.strip() for x in authors if '@' in x ]
		except IOError:
			return []
		finally:
			f.close()
			f = None


	def get_license(self):
		"""little function that pulls the license from a text file."""
		try:
			f = open('COPYING', 'r')
			license = f.read()
			return license
		except IOError:
			return None
		finally:
			f.close()
			f = None


	# WORKING LOOP ########################################################
	def loop(self):
		"""main loop for eva that runs the business logic, etc..."""

		self.log.debug('entering local loop()')
		sleep = idle.timeleft(config.IDLELIMIT)	# sleep time in seconds

		e = exclusions.exclusions(yamlconf=config.THECONFIG)
		# do the check, and it it passes get the good value.
		result = e.is_fileok()
		if result: result = e.is_excluded()
		# otherwise it's false anyways! not excluded!
		else:
			self.log.warn('problem with config file.')
			self.log.warn('assuming no exclusions.')

		# if not excluded
		if not result:
			self.log.warn('you are currently NOT excluded from idle-logoff.')

			if idle.is_idle(config.IDLELIMIT):

				self.log.info('user is currently idle.')
				if self.warned:

					# how long have we been warned for ?
					timedelta = datetime.datetime.today() - self.warned
					self.delta = int(math.ceil(timedelta.seconds + (timedelta.days*24*60*60) + (timedelta.microseconds*(1/1000000))))
					# if warning time is up!
					if self.delta > config.COUNTDOWN:

						self.log.fatal('you are being logged off due to inactivity.')
						self.msg(title='you are currently idle',
						message='you are being logged off due to inactivity',
						urgency=pynotify.URGENCY_CRITICAL,
						timeout=pynotify.EXPIRES_NEVER)
						#TODO: DO_LOGOFF()
						return False

					else:
						# change the +0 to +1 if you run
						# on a pentium three-zillion cpu
						# and it can do lots of loops in
						# a fraction of a second. the +0
						# is slightly more accurate math
						sleep = self.delta+0

				# do warn
				else:
					self.warned = datetime.datetime.today()
					timeleft = config.COUNTDOWN - self.delta
					self.log.warn('you are currently idle. rectify this or your session will be automatically logged off.')
					self.msg(title='You are currently idle',
					message='your session will be logged off in about %d seconds (and counting) if you continue to be idle.' % (timeleft) + os.linesep + 'press a key or move your mouse to cancel the impending logoff.',
					urgency=pynotify.URGENCY_CRITICAL,
					timeout=pynotify.EXPIRES_NEVER)

					# sleep less often (to see if someone
					# taps a mouse) but make sure that we
					# wake up in time before countdown is up
					# a faster sleep updates the countdown
					# counter faster, but wastes more cpu.
					sleep = min(timeleft, config.FASTSLEEP)


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
			self.log.info('you are currently excluded from idle-logoff.')
			if self.warned:
				self.log.info('log off canceled, you\'ve just been excluded.')
				self.msg(message='log off canceled, you\'ve just been excluded.',
				title=None,
				urgency=pynotify.URGENCY_LOW,
				timeout=pynotify.EXPIRES_DEFAULT)
				self.warned = False

			#sleep = config.SLEEPTIME	# CHANGED IN FAVOUR OF:
			sleep = max(idle.timeleft(config.IDLELIMIT), self.get_exclusions_changed_time())

		e = None			# clean up the object

		sleep = max(1, sleep)		# sleep for at least one second
		self.log.info('going to sleep for %d seconds.' % sleep)

		# add a new timeout so this gets called again
		self.source_id = gobject.timeout_add(sleep*1000, self.loop)

		# this loop ends, and we wait for the above rescheduled event
		return False

	def get_exclusions_changed_time(self):
		# FIXME: make this ideally check the next time the exclusions are
		# liable to include the user (by parsing and looking at date/time
		# if possible. if this is too hard (which it could be) then sleep
		# for some constant amount of time shown below. also, add a watch
		# on the exclusions file, and if it changes, then wake up and see
		# if the exclusions are now enough to let someone get logged off!
		return config.SLEEPTIME


	# MAIN ################################################################
	def main(self):
		"""main to run for the class."""
		# TODO: attach a signal for mouse movement to some function
		# which updates the "your machine is idle" dialog whenever it
		# is called. i think this is possible because of this link:
		# http://library.gnome.org/devel/gobject/unstable/signal.html
		# UPDATE: actually it might not be possible because it relies
		# on the motion-notify-event of a gtkwidget object which we
		# won't have access to. (there is just the icon and pynotify)


		# make the notify work
		if not pynotify.init(self.name):
			# FIXME: fall back to a different messaging alternative.
			sys.exit(1)

		# run informational welcome message script.
		gobject.idle_add(self.info)

		# start it off in one second from now.
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
