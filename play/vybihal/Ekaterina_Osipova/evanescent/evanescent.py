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

# NOTES ########################################################################
# * this script should be run on each machine at boot
# * this script hasn't been designed to avoid killing things like:
#	- long running user processes (eg: $ sleep 13h && echo 'hi mom')
#	- detached screen sessions (no line will be seen connected)
#	- long compute scripts should be run on linux.cs.mcgill.ca ($ ./my_big_c.py)
# * this script checks for exclusions at IDLELIMIT, but once the user is warned,
# we don't check the exclusions again between IDLELIMIT and IDLELIMIT+COUNTDOWN
################################################################################

# FIXME/TODO: go through all the files and fix all the FIXME's and do all the TODO's
# FIXME: mouse movement doesn't un-idle a machine (BUG/FEATURE ?)
# TODO: kill idle users on a non-idle machine (OPTIONAL)
# TODO: check if LOCAL7 facility works on LOGMASTER
# TODO: clean up info/debug messages and make them more sensible/informative
# TODO: have script fail on startup if all the necessary modules aren't installed (ex: python-utmp, yaml)
# TODO: add a big try/except around the main script if possible to catch and log hidden script errors
# TODO: pull in configuration file values from a remote file using wget or similar (idea from rgws@cs.mcgill.ca)
# TODO: check that the license one liner program description is correct at the top of each file.
# TODO: make an evanescent error class, and create specific errors for all the random evanescent things.
# TODO: instead of always logging to dialog, log things into better categories. daemon stuff always goes there, etc...
# TODO: clean up all message strings and add %s data within them, and rewrite them to be clear and clean.
# TODO: we could add an exclusion option for a particular process or program name. eg if program my_proc.py is running, don't shutdown.

import os				# for posix/nt detection
import sys				# for sys.exit()
import math				# for math.ceil()
import datetime				# for time diffs
import time				# for sleep() and time()
import logging, logging.handlers	# for syslog stuff
import getpass				# for eva loop
import exclusions			# i wrote this one
import idle				# i wrote this one
import misc				# i wrote this one
import yamlhelp				# i wrote this one
import eerror				# custom exceptions classes

if os.name in ['posix']:
	import signal			# for signal stuff for linux

# FIXME: this file should only be included for linux, however since
# there is a daemon.Error that is used in a try-except, windows
# scripts fail since they look for this value even though it is never used.
import daemon			# i wrote this one

if os.name in ['nt']:
	import decode			# decode library for encoded files
	import encoded			# list of encoded files

# TODO: do some sort of INIT on config from evanescent init so that the name variable from evanescent gets passed and used in config.
import config				# import configs

class evanescent:

	def __init__(self, name=None, start=None):
		# name to be used as in script as main identifier
		if name is None: name = 'evanescent'	# FIXME: remove this line. it is a temporary fix until the above works on windows.
		# FIXME: the below name finder doesn't work on windows. FIX THAT.
		if name is None: name = os.path.splitext(__file__)[0]

		self.name = str(name)

		# run evanescent in a special mode
		self.start = str(start)

		# logging variables
		self.log = None	# main logger
		self.logh = {}	# log handles
		self.logs = {}	# other log handles


	def sigusr1(self, signum, frame):
		"""signal handler for sigusr1"""
		#raise KeyboardInterrupt
		self.logs['dialog'].debug('caught signal: sigusr1')


	def sigusr2(self, signum, frame):
		"""signal handler for sigusr2"""
		self.logs['dialog'].debug('caught signal: sigusr2')


	def main(self):
		"""this main function runs all the startup code, and then kicks off evanescent.
		it logs all its errors to the main log. it also runs sys.exit() when needed."""

		# should evanescent be disabled, and exit right away?
		if not(config.STARTMEUP): sys.exit(0)

		# setup the logging handles
		self.logging()

		# setup signal handling
		if os.name in ['posix']:
			# read: $ man 7 signal
			signal.signal(signal.SIGUSR1, signal.SIG_IGN)	# ignore
			signal.signal(signal.SIGUSR2, signal.SIG_IGN)	# ignore

		# run this on first start to check for errors...
		# this avoids us having to wait for a machine to be idle before is_excluded() runs
		e = exclusions.exclusions(config.THECONFIG)
		if not(e.syntax_ok()):
			message = e.syntax_ok(message=True)
			self.log.fatal('syntax error in config file, exiting.')
			self.log.fatal(str(message))
			sys.exit(1)
		e = None

		# make all the special directories we might need
		try:
			if not(os.path.exists(config.SHAREDDIR)): os.makedirs(config.SHAREDDIR)

			# make directory for putting shared messages
			d = os.path.join(config.SHAREDDIR, config.MSGSUBDIR)
			if not(os.path.exists(d)): os.makedirs(d)

			if os.name in ['nt']:
				# make idle time reporting directory
				d = os.path.join(config.SHAREDDIR, config.WIDLEPATH)
				if not(os.path.exists(d)): os.makedirs(d)

		except IOError, e:
			self.log.fatal('error making directories, exiting.')
			self.log.debug('error:%s%s' % (os.linesep, e))
			sys.exit(1)

		# extract all the special files we might need
		if not(self.decode()):
			self.log.fatal('error decoding files, exiting.')
			sys.exit(1)

		# record which start mode we're running in.
		self.log.debug('start is: %s' % str(self.start))

		# which loop do we want to run?
		if self.start == 'eva_loop': start_func = self.eva_loop
		#elif self.start == 'main_loop': start_func = self.main_loop
		else: start_func = self.main_loop

		# create daemon object
		if os.name in ['posix']:
			d = daemon.daemon(pidfile=config.DAEMONPID, start_func=start_func, logger=self.logs['daemon'], close_fds=not(config.DEBUGMODE))

		try:
			if os.name in ['posix']: d.start_stop()
			elif os.name in ['nt']: start_func()
			else: raise AssertionError('os: `%s\' is not supported at this time.' % os.name)

		except KeyboardInterrupt, e:
			if os.name in ['posix']: d.start_stop([sys.argv[0], 'stop'])
			elif os.name in ['nt']:
				# VERIFY: it's possible that a KeyboardInterrupt gets generated when Control-Alt-Delete is pressed on user-login
				# TODO: if e == 'some special thing that wasn't a standard control-c press then:' #main_loop()
				pass

		except daemon.DaemonError, e:
			self.log.fatal('daemon error: %s' % e)
			sys.exit(1)

		except SystemExit:
			pass

		except:
			# special logfile for if something bad happens
			import traceback
			self.log.fatal('fatal exception:\n%s' % traceback.format_exc())
			try:
				traceback.print_exc(file=open(config.MYERRPATH, 'w+'))
			except IOError, (n, e):
				# we don't have permission to write the MYERRPATH log file.
				# 'Permission denied'
				if e == 13:
					pass


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
		if os.name in ['nt']:
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
		self.logs['daemon'] = logging.getLogger('%s.daemon' % self.name)
		self.logs['dialog'] = logging.getLogger('%s.dialog' % self.name)
		self.logs['signal'] = logging.getLogger('%s.signal' % self.name)
		self.logs['evalog'] = logging.getLogger('%s.evalog' % self.name)

		# send a hello message
		self.log.debug('hello from %s' % self.name)


	def decode(self):
		"""do the decoding. is currently only used for nt."""
		# decode previously encoded special files for windows
		# the reason we do this is so that we can package all
		# the files that we need for the program as .py which
		# lets us bundle them nicely using setup tools stuff.
		# if we want this code to be used for other platforms
		# besides windows, then we might need to modify it to
		# support some extra settings, and folder parameters.
		if os.name in ['nt']:
			c = 0
			for f in encoded.encoded:
				try:
					decode.decode(f, nline=encoded.nline[c])
				except eerror.DecodeError, e:
					self.log.error('decode error: `%s\'' % e)
					return False
				c = c + 1

		return True


	def main_loop(self):
		"""this is the main loop for evanescent."""

		# clean directory for putting shared messages
		d = os.path.join(config.SHAREDDIR, config.MSGSUBDIR)
		if os.path.exists(d):
			for x in os.listdir(d):
				try:
					os.remove(os.path.join(d, x))
				except OSError:
					pass

		if os.name in ['nt']:
			# clean idle time reporting directory
			d = os.path.join(config.SHAREDDIR, config.WIDLEPATH)
			if os.path.exists(d):
				for x in os.listdir(d):
					try:
						os.remove(os.path.join(d, x))
					except OSError:
						pass

		warned = False
		sleep = config.SLEEPTIME

		# create idle time object
		# we don't want to tick, because we want the
		# same snapshot inside the entire loop.
		# tick once per loop to refresh the snapshot.
		i = idle.idle(tick_default=False, me=None)	# [nt] me==None: get current idle data and others

		# main loop
		self.logs['dialog'].debug('entering main loop')
		while True:

			i.tick(True)	# refresh idle data

			# extract for do_broadcast()
			extract = i.idle()

			# if entire machine is idle
			if i.is_idle(threshold=config.IDLELIMIT):
				self.logs['dialog'].info('computer is idle')

				if warned:
					# we've waited this long since users got warned
					timedelta = datetime.datetime.today() - warned
					delta = int(math.ceil(timedelta.seconds + (timedelta.days*24*60*60) + (timedelta.microseconds*(1/1000000))))
					# if warning time is up!
					if delta > config.COUNTDOWN:
						self.logs['dialog'].warn('machine shutting down now!')

						# returns true or false if this worked
						if not(misc.do_nologin('sorry, machine is shutting down')):
							self.logs['dialog'].warn('running: do_nologin() failed.')

						# broadcasts a write to all the cli/gtk clients to say goodbye
						misc.do_broadcast('machine is going down now', {'users': extract['users'], 'line': extract['line']})
						misc.do_shutdown()	# kills the system
						# FIXME: if the tdcommand is something like suspend, then we have a problem when the machine wakes up.
						sys.exit(0)

					else:
						# TODO: maybe we check for users pressing cancel here?
						self.logs['dialog'].debug('waiting for countdown to be up')
						pass

				else:

					e = exclusions.exclusions(config.THECONFIG)
					self.logs['dialog'].debug('checking exclusions...')
					try:
						# from the time when a machine comes up, give users a chance of `INITSLEEP' seconds
						# to login before the empty machine is considered idle and shuts itself down.
						# idea for this feature from andrewb@cs.mcgill.ca
						uptime = misc.uptime()
						if config.INITSLEEP > 0 and uptime < config.INITSLEEP:
							self.logs['dialog'].debug('machine just booted, excluding from shutdown')
							sleep = abs(config.INITSLEEP - uptime)	# abs to be safe

						# if we should shutdown
						elif not(e.is_excluded(users=i.unique_users())):

							self.logs['dialog'].debug('machine isn\'t excluded, doing warn')
							# now we warn users of impending shutdown
							misc.do_broadcast('machine is shutting down in %d seconds if you continue to be idle. tap any key to cancel impending shutdown.' % config.COUNTDOWN, {'users': extract['users'], 'line': extract['line']})
							warned = datetime.datetime.today()

							# sleep less often (to see if someone will tap a mouse)
							# but also make sure that we wake up in time before countdown is up
							sleep = min(config.COUNTDOWN, config.FASTSLEEP)

						else:
							self.logs['dialog'].debug('machine is excluded')
							# fix the sleep value back to normal-ness
							# FIXME: technically, we could do the min thing and wake up
							# in time to see another user go idle, but the exclusions
							# might still hold, so we'll assume they are sane; eg:
							# exclusions that vary from minute to minute would make this act funny.
							sleep = config.SLEEPTIME

					except SyntaxError, e:
						# FIXME: improve the config parser checker code
						self.logs['dialog'].critical('syntax error in live config file!')
						self.logs['dialog'].critical('e: %s' % e)
						self.logs['dialog'].critical('FIXME: need to improve the config parser checker code')
						sys.exit(1)

					e = None	# free memory

			else:	# not idle
				self.logs['dialog'].debug('computer is not idle')
				self.logs['dialog'].debug('active users are:')
				notidle = i.active_indices(threshold=config.IDLELIMIT)
				for x in notidle:
					self.logs['dialog'].debug('user: %s; line: %s; idle: %s' % (i.get_user(x), i.get_line(x), str(i.get_idle(x))[0:4]))

				# idle
				areidle = i.idle_indices(threshold=config.IDLELIMIT)
				if len(areidle) > 0: self.logs['dialog'].debug('idle users are:')
				for x in areidle:
					self.logs['dialog'].debug('user: %s; line: %s; idle: %s' % (i.get_user(x), i.get_line(x), str(i.get_idle(x))[0:4]))


				# datetime objects should return true
				if warned:
					# shutdown was canceled, computer no longer idle
					self.logs['dialog'].info('shutdown canceled, not idle anymore')
					warned = False
					misc.do_broadcast('impending shutdown was canceled.', {'users': extract['users'], 'line': extract['line']})

				else:
					pass
					# if we want to get rid of idle users even though the entire machine isn't idle
					# TODO:
					#DO: if i.ls_idle() ...
					#STILL NEED TO CHECK EXCLUSIONS, AND HAVE SOME SORT OF POLICY ON IF THEY APPLY.
					#MAYBE RUN A SECOND EXCLUSION LOG FILE LIKE: E2.yaml.conf including policies for idle users.

				# the min time is the longest we're going to have to wait for everyone to go idle
				# however, this would be less if someone logs off prematurely. to avoid this problem,
				# we need to listen for log off events and wake up when one occurs.
				m = int(math.ceil(i.min_idle()))
				diff = config.IDLELIMIT - m

				if diff < config.SLEEPTIME:
					sleep = diff + 1
				else:
					sleep = config.SLEEPTIME

			# TODO: read some fd with select or listen for some signal that fires on a user logout event
			# check online to see if the logout command broadcasts something ?
			# we could select() on the utmp file and wake up everytime it changes
			# we could get the /etc/gdm/PostSession script to run a kill -USR2 signal to poke this program
			# we could select() on the /var/log/auth log file to check for sshd session closed events
			# there are pam session events that get triggered. look into pam session for more info.

			# easy sleep
			#time.sleep(sleep)


			# TODO: use select if we can wait for some FD giving us client information...
			# select.select(some_fd_saying_if_someone_pressed_a_button)


			# this block sleeps nicely and catches signals too...


			# TODO: two signals:
			# 1) POKE to get code to loop and re-read config file (eg, from an admin)
			# 2) SHHH (a signal from a user saying hey, i pressed cancel) -> our program can send this if they click a cancel button

			# if we sleep for zero seconds or less, this can often make the sleep call hang forever
			sleep = int(math.ceil(sleep))
			if sleep > 0:
				# allow/handle incoming signals
				self.logs['dialog'].debug('going to sleep for %s seconds' % sleep)

				if os.name in ['posix']:
					caught = False
					signal.signal(signal.SIGUSR1, self.sigusr1)	# handle
					signal.signal(signal.SIGUSR2, self.sigusr2)	# handle

					def handler(signum, frame):
						"""internal sleep handler function"""
						raise KeyboardInterrupt

					signal.signal(signal.SIGALRM, handler)
					signal.alarm(sleep)

					try:
						signal.pause()
						# pause exited, so a signal was caught
						self.logs['dialog'].debug('signal caught!')
						caught = True
					except KeyboardInterrupt:
						# exception happened, so alarm caused this
						caught = False
						self.logs['dialog'].debug('sleep over, waking up!')

					# we continue...
					signal.alarm(0)		# disable the alarm
					signal.signal(signal.SIGUSR1, signal.SIG_IGN)	# ignore
					signal.signal(signal.SIGUSR2, signal.SIG_IGN)	# ignore

				# windows or otherwise...
				else:
					try:
						time.sleep(sleep)
					except IOError, e:
						# maybe someone pressed Control-Alt-Delete after
						# script was already running on system startup
						self.logs['dialog'].debug('ioerror while sleeping: %s' % str(e))


	def eva_loop(self):
		"""this is the main loop for eva."""
		# note: we're using getpass.getuser() instead of os.getlogin() because the later isn't platform compatible.
		f = yamlhelp.yamlhelp(os.path.join(config.SHAREDDIR, config.MSGSUBDIR, getpass.getuser()))
		if os.name in ['posix']:
			# TODO: import a messaging class for posix. maybe pynotify?
			pass

		if os.name in ['nt']:
			i = idle.idle(tick_default=False, me=True)
			g = yamlhelp.yamlhelp(os.path.join(config.SHAREDDIR, config.WIDLEPATH, getpass.getuser()))

			import wpyqtmsg
			msg = wpyqtmsg.wpyqtmsg(config.ICONIMAGE)

		last_message = -1

		self.logs['evalog'].debug('entering eva loop')
		while True:
			# if we are a windows client, then we need to `report'
			# our idle time for the main evanescent process which
			# won't be able to read it on its own.
			if os.name in ['nt']:
				self.logs['evalog'].debug('now reporting idle time')
				g.put_yaml({'tsync': time.time(), 'widle': i.idle(tick=True)})

			# if there are any messages to display, then display them
			m = os.path.join(config.SHAREDDIR, config.MSGSUBDIR, getpass.getuser())
			if os.path.exists(m):
				self.logs['evalog'].debug('the message bank is not empty')
				d = f.get_yaml()
				# there should be an array of messages in yaml
				if type(d) == type([]):
					for x in d:
						# if the next message in line is newer than what we've seen so far...
						if last_message < x['id']:
							last_message = x['id']

							# check if messages are `stale'. eg from a previous login/logout.
							if (time.time() - x['tsync']) < config.STALETIME:
								self.logs['evalog'].info('message: %s' % x['msg'])
								if os.name in ['nt']: msg.msg('evanescent', x['msg'])	# send qt4 pop up msg
								elif os.name in ['posix']: pass				# send a pynotify msg
								time.sleep(config.READSLEEP)				# sleep time b/w msgs
						else:
							# TODO: potentially we could prune the file by removing this message.
							pass

			# go around the loop
			self.logs['evalog'].debug('going to sleep for %s seconds' % config.FASTSLEEP)
			time.sleep(config.FASTSLEEP)


if __name__ == "__main__":

	e = evanescent()
	e.main()

