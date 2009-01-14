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

"""
* this script should be run on each machine at boot
* this script hasn't been designed to avoid killing things like:
	- long running user processes (eg: $ sleep 13h && echo 'hi mom')
- detached screen sessions (no line will be seen connected)
	- long compute scripts should be run on linux.cs.mcgill.ca ($ ./my_big_c.py)
* this script checks for exclusions at IDLELIMIT, but once the user is warned,
we don't check the exclusions again between IDLELIMIT and IDLELIMIT+COUNTDOWN
"""

# FIXME/TODO: go through all the files and fix all the FIXME's and do all the TODO's
# FIXME: mouse movement doesn't un-idle a machine (BUG/FEATURE ?)
# TODO: kill idle users on a non-idle machine (OPTIONAL)
# TODO: check if LOCAL7 facility works on LOGMASTER
# TODO: clean up info/debug messages and make them more sensible/informative
# TODO: have script fail on startup if all the necessary modules aren't installed (ex: python-utmp, yaml)
# TODO: add a big try/except around the main script if possible to catch and log hidden script errors
# TODO: pull in configuration file values from a remote file using wget or similar (idea from rgws@cs.mcgill.ca)
# TODO: check that the license one liner program description is correct at the top of each file.

import os				# for posix/nt detection
import sys				# for sys.exit()
import math				# for math.ceil()
import signal				# for signal stuff
import datetime				# for time diffs
import time				# for sleeping in windows
import logging, logging.handlers	# for syslog stuff
import daemon				# i wrote this one
import exclusions			# i wrote this one
import idle				# i wrote this one
import misc				# i wrote this one

import config				# import configs

"""
*	logging errors:
-	CRITICAL
-	FATAL
-	ERROR
-	WARN
-	INFO
-	DEBUG
"""

def evanescent():
	"""this is the main function for the evanescent daemon"""

	# run this on first start to check for errors...
	# this avoids us having to wait for a machine to be idle before is_excluded runs
	e = exclusions.exclusions(config.THECONFIG)
	if not(e.syntax_ok()):
		message = e.syntax_ok(message=True)
		evalog_logger.fatal('syntax error in config file')
		evalog_logger.fatal(str(message))
		sys.exit(1)
	e = None

	warned = False
	sleep = config.SLEEPTIME
	# main loop (polling)
	evalog_logger.debug('entering main loop')
	while True:

		i = idle.idle(tick_default=False)
		extract = i.idle()	# extract for do_broadcast()
		# if entire machine is idle
		if i.is_idle(threshold=config.IDLELIMIT):
			evalog_logger.info('computer is idle')

			if warned:
				# we've waited this long since users got warned
				timedelta = datetime.datetime.today() - warned
				delta = int(math.ceil(timedelta.seconds + (timedelta.days*24*60*60) + (timedelta.microseconds*(1/1000000))))
				# if warning time is up!
				if delta > config.COUNTDOWN:
					evalog_logger.warn('machine shutting down now!')
					misc.do_nologin('sorry, machine is shutting down')	# returns true or false if this worked
					# broadcasts a write to all the cli/gtk clients to say goodbye
					misc.do_broadcast('machine is going down now', {'users': extract['users'], 'line': extract['line']})
					misc.do_shutdown()	# kills the system
					sys.exit(0)

				else:
					# TODO: maybe we check for users pressing cancel here?
					evalog_logger.debug('waiting for countdown to be up')
					pass

			else:

				e = exclusions.exclusions(config.THECONFIG)
				evalog_logger.debug('checking exclusions...')
				try:
					# from the time when a machine comes up, give users a chance of `INITSLEEP' seconds
					# to login before the empty machine is considered idle and shuts itself down.
					# idea for this feature from andrewb@cs.mcgill.ca
					uptime = misc.uptime()
					if config.INITSLEEP > 0 and uptime < config.INITSLEEP:
						evalog_logger.debug('machine just booted, excluding from shutdown')
						sleep = abs(config.INITSLEEP - uptime)	# abs to be safe

					# if we should shutdown
					elif not(e.is_excluded(users=i.unique_users())):

						evalog_logger.debug('machine isn\'t excluded, doing warn')
						# now we warn users of impending shutdown
						misc.do_broadcast('machine is shutting down in %d seconds if you continue to be idle. tap any key to cancel impending shutdown.' % config.COUNTDOWN, {'users': extract['users'], 'line': extract['line']})
						warned = datetime.datetime.today()

						# sleep less often (to see if someone will tap a mouse)
						# but also make sure that we wake up in time before countdown is up
						sleep = min(config.COUNTDOWN, config.FASTSLEEP)

					else:
						evalog_logger.debug('machine is excluded')
						# fix the sleep value back to normal-ness
						# FIXME: technically, we could do the min thing and wake up
						# in time to see another user go idle, but the exclusions
						# might still hold, so we'll assume they are sane; eg:
						# exclusions that vary from minute to minute would make this act funny.
						sleep = config.SLEEPTIME


				except SyntaxError, e:
					# FIXME: improve the config parser checker code
					evalog_logger.critical('syntax error in live config file!')
					evalog_logger.critical('e: %s' % e)
					evalog_logger.critical('FIXME: need to improve the config parser checker code')
					sys.exit(1)

				e = None	# free memory



		else:	# not idle
			evalog_logger.debug('computer is not idle')
			notidle = i.active_indices(threshold=config.IDLELIMIT)
			evalog_logger.debug('user: %s' % ', '.join(i.get_user(notidle)))
			evalog_logger.debug('line: %s' % ', '.join(i.get_line(notidle)))
			evalog_logger.debug('idle: %s' % ', '.join(map(str, i.get_idle(notidle))))

			# datetime objects should return true
			if warned:
				# shutdown was canceled, computer no longer idle
				evalog_logger.info('shutdown canceled, not idle anymore')
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


		i = None	# free memory

		# TODO: read some fd with select or listen for some signal that fires on a user logout event
		# check online to see if the logout command broadcasts something ?
		# we could select() on the utmp file and wake up everytime it changes
		# we could get the /etc/gdm/PostSession script to run a kill -USR2 signal to poke this program
		# we could select() on the /var/log/auth log file to check for sshd session closed events

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
			evalog_logger.debug('going to sleep for %s seconds' % sleep)

			if os.name in ['posix']:
				caught = False
				signal.signal(signal.SIGUSR1, sigusr1)	# handle
				signal.signal(signal.SIGUSR2, sigusr2)	# handle

				def handler(signum, frame):
					"""internal sleep handler function"""
					raise KeyboardInterrupt

				signal.signal(signal.SIGALRM, handler)
				signal.alarm(sleep)

				try:
					signal.pause()
					# pause exited, so a signal was caught
					evalog_logger.debug('signal caught!')
					caught = True
				except KeyboardInterrupt:
					# exception happened, so alarm caused this
					caught = False
					evalog_logger.debug('sleep over, waking up!')

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
					#DEBUG: open(config.MYERRPATH+str('4'), 'w+').write(str(e))
					pass

def sigusr1(signum, frame):
	#raise KeyboardInterrupt
	evalog_logger.debug('someone poked me, waking up!')


def sigusr2(signum, frame):
	pass

if __name__ == "__main__":

	if not(config.STARTMEUP): sys.exit(0)

	if os.name in ['posix']:
		# read: $ man 7 signal
		signal.signal(signal.SIGUSR1, signal.SIG_IGN)	# ignore
		signal.signal(signal.SIGUSR2, signal.SIG_IGN)	# ignore

	# decode previously encoded special files for windows
	# the reason we do this is so that we can package all
	# the files that we need for the program as .py which
	# lets us bundle them nicely using setup tools stuff.
	if os.name in ['nt']:
		import decode
		import encoded
		c = 0
		for f in encoded.encoded:
			decode.decode(f, nline=encoded.nline[c])
			c = c + 1

	# everyone uses this format
	#logging.basicConfig(level=logging.DEBUG, format=config.LOGFORMAT)
	formatter = logging.Formatter(config.LOGFORMAT)

	# handler for local disk
	# FIXME: check file permission for log file before this line runs
	try:
		RotatingFileHandler = logging.handlers.RotatingFileHandler(config.MYLOGPATH, maxBytes=1024*100, backupCount=9)
	except IOError:
		message = "can't open log file for writing (are you root?)"
		sys.stderr.write(message + "\n")
		sys.exit(1)
	RotatingFileHandler.setFormatter(formatter)

	# handler for global logging server
									#logging.handlers.SysLogHandler.LOG_DAEMON (does this even work? i can't find the logs...)
	SysLogHandler = logging.handlers.SysLogHandler(config.LOGSERVER, logging.handlers.SysLogHandler.LOG_LOCAL7)	# TODO: find a way to change the facility to 'evanescent'
	SysLogHandler.setFormatter(formatter)

	# name a log route, set a level, add handlers
	l = logging.getLogger('evanescent')
	if config.WORDYMODE: l.setLevel(logging.DEBUG)
	else: l.setLevel(logging.WARN)
	l.addHandler(RotatingFileHandler)
	l.addHandler(SysLogHandler)

	# handlers in x propagate down to everyone (y) in the x.y tree
	daemon_logger = logging.getLogger('evanescent.daemon')
	evalog_logger = logging.getLogger('evanescent.evalog')
	signal_logger = logging.getLogger('evanescent.signal')

	l.debug('hello from evanescent')		# send a hello message
	#daemon_logger.info('hi from daemon')		# send a hello message

	if os.name in ['posix']: d = daemon.daemon(pidfile=config.DAEMONPID, start_func=evanescent, logger=daemon_logger, close_fds=not(config.DEBUGMODE))
	try:
		if os.name in ['posix']: d.start_stop()
		elif os.name in ['nt']: evanescent()
		else: raise AssertionError('os: `%s\' is not supported at this time.' % os.name)
	except KeyboardInterrupt, e:
		if os.name in ['posix']: d.start_stop([sys.argv[0], 'stop'])
		elif os.name in ['nt']:
			# VERIFY: it's possible that a KeyboardInterrupt gets generated when Control-Alt-Delete is pressed on user-login
			# TODO: if e == 'some special thing that wasn't a standard control-c press then:' #evanescent()
			pass
	except SystemExit:
		pass
	except:
		import traceback
		traceback.print_exc(file=open(config.MYERRPATH, 'w+'))

