#!/usr/bin/python
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
# TODO: add GPL license info at the top of all the files
# TODO: add a big try/except around the main script if possible to catch and log hidden script errors

import sys				# for sys.exit()
import math				# for math.ceil()
import signal				# for signal stuff
import datetime				# for time diffs
import logging, logging.handlers	# for syslog stuff
import daemon				# i wrote this one
import exclusions			# i wrote this one
import idle				# i wrote this one
import misc				# i wrote this one

from config import *			# import to globals

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
	e = exclusions.exclusions(THECONFIG)
	if not(e.syntax_ok()):
		evalog_logger.fatal('syntax error in config file')
		sys.exit(1)
	e = None

	warned = False
	sleep = SLEEPTIME
	# main loop (polling)
	evalog_logger.debug('entering main loop')
	while True:

		i = idle.idle(tick_default=False)
		extract = i.idle()	# extract for do_broadcast()
		# if entire machine is idle
		if i.is_idle(threshold=IDLELIMIT):
			evalog_logger.info('computer is idle')

			if warned:
				# we've waited this long since users got warned
				timedelta = datetime.datetime.today() - warned
				delta = int(math.ceil(timedelta.seconds + (timedelta.days*24*60*60) + (timedelta.microseconds*(1/1000000))))
				# if warning time is up!
				if delta > COUNTDOWN:
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

				e = exclusions.exclusions(THECONFIG)
				evalog_logger.debug('checking exclusions...')
				try:
					# if we should shutdown
					if not(e.is_excluded(users=i.unique_users())):

						evalog_logger.debug('machine isn\'t excluded, doing warn')
						# now we warn users of impending shutdown
						misc.do_broadcast('machine is shutting down in %d seconds if you continue to be idle. tap any key to cancel impending shutdown.' % COUNTDOWN, {'users': extract['users'], 'line': extract['line']})
						warned = datetime.datetime.today()

						# sleep less often (to see if someone will tap a mouse)
						# but also make sure that we wake up in time before countdown is up
						sleep = min(COUNTDOWN, FASTSLEEP)

					else:
						evalog_logger.debug('machine is excluded')
						# fix the sleep value back to normal-ness
						# FIXME: technically, we could do the min thing and wake up
						# in time to see another user go idle, but the exclusions
						# might still hold, so we'll assume they are sane; eg:
						# exclusions that vary from minute to minute would make this act funny.
						sleep = SLEEPTIME


				except SyntaxError, e:
					# FIXME: improve the config parser checker code
					evalog_logger.critical('syntax error in live config file!')
					evalog_logger.critical('FIXME: need to improve the config parser checker code')
					sys.exit(1)

				e = None	# free memory



		else:	# not idle
			evalog_logger.debug('computer is not idle')
			notidle = i.active_indices(threshold=IDLELIMIT)
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
			diff = IDLELIMIT - m

			if diff < SLEEPTIME:
				sleep = diff + 1
			else:
				sleep = SLEEPTIME


		i = None	# free memory

		# TODO: read some fd with select that looks for a user logout event

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


def sigusr1(signum, frame):
	#raise KeyboardInterrupt
	evalog_logger.debug('someone poked me, waking up!')


def sigusr2(signum, frame):
	pass

if __name__ == "__main__":

	# read: $ man 7 signal
	signal.signal(signal.SIGUSR1, signal.SIG_IGN)	# ignore
	signal.signal(signal.SIGUSR2, signal.SIG_IGN)	# ignore

	# everyone uses this format
	#logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)
	formatter = logging.Formatter(LOGFORMAT)

	# handler for local disk
	# FIXME: check file permission for log file before this line runs
	try:
		RotatingFileHandler = logging.handlers.RotatingFileHandler(MYLOGPATH, maxBytes=1024*100, backupCount=9)
	except IOError:
		message = "can't open log file for writing (are you root?)"
		sys.stderr.write(message + "\n")
		sys.exit(1)
	RotatingFileHandler.setFormatter(formatter)

	# handler for global logging server
									#logging.handlers.SysLogHandler.LOG_DAEMON (does this even work? i can't find the logs...)
	SysLogHandler = logging.handlers.SysLogHandler(LOGSERVER, logging.handlers.SysLogHandler.LOG_LOCAL7)	# TODO: find a way to change the facility to 'evanescent'
	SysLogHandler.setFormatter(formatter)

	# name a log route, set a level, add handlers
	l = logging.getLogger('evanescent')
	if WORDYMODE: l.setLevel(logging.DEBUG)
	else: l.setLevel(logging.WARN)
	l.addHandler(RotatingFileHandler)
	l.addHandler(SysLogHandler)

	# handlers in x propagate down to everyone (y) in the x.y tree
	daemon_logger = logging.getLogger('evanescent.daemon')
	evalog_logger = logging.getLogger('evanescent.evalog')
	signal_logger = logging.getLogger('evanescent.signal')

	l.debug('log says hi')				# send a hello message

	#daemon_logger.info('hi from daemon')		# send a hello message

	d = daemon.daemon(pidfile=DAEMONPID, start_func=evanescent, logger=daemon_logger, close_fds=not(DEBUGMODE))
	d.start_stop()

