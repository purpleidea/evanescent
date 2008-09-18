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

# TODO: kill idle users on a non-idle machine (OPTIONAL)

import sys				# for sys.exit()
import math				# for math.ceil()
import signal				# for signal stuff
import logging, logging.handlers	# for syslog stuff
import daemon				# i wrote this one
import exclusions			# i wrote this one
import idle				# i wrote this one
import misc				# i wrote this one

DEBUGMODE = True			# debug mode
IDLELIMIT = 60*60			# 1 hour before you're idle
COUNTDOWN = 5*60			# five minute countdown before shutdown
SLEEPTIME = 10*60			# check every 10 minutes
FASTSLEEP = 1*60			# how often do we poll after the user has been warned
THECONFIG = 'idle.conf.yaml'		# the config file
LOGSERVER = ('logmaster', 514)		# syslog server
DAEMONPID = '/var/run/evanescent.pid'	# pid file for daemon
MYLOGPATH = '/var/log/evanescent.log'	# path for local log file
LOGFORMAT = '%(asctime)s %(levelname)-8s %(name)-16s %(message)s'

"""
# logging errors:
CRITICAL
FATAL
ERROR
WARN
INFO
DEBUG
"""

def evanescent():
	"""this is the main function for the evanescent daemon"""

	# run this on first start to check for errors...
	# this avoids us having to wait for a machine to be idle before is_excluded runs
	e = exclusions.exclusions(THECONFIG)
	if not(e.syntax_ok()):
		raise SyntaxError, 'problem with syntax in config file'
	e = None

	warned = False
	sleep = SLEEPTIME
	# main loop (polling)
	while True:

		i = idle.idle()
		# if entire machine is idle
		if i.is_idle(threshold=IDLELIMIT):

			if warned:

				# we've waited this long since users got warned
				timedelta = datetime.datetime.today() - warned
				delta = int(math.ceil(timedelta.seconds + (timedelta.days*24*60*60) + (timedelta.microseconds*(1/1000000))))
				# if warning time is up!
				if delta > COUNTDOWN:
					misc.do_nologin('sorry, machine is shutting down')	# returns true of false if this worked
					misc.do_broadcast('machine is going down now')		# broadcasts a write to all the cli/gtk clients to say goodbye
					misc.do_shutdown()	# kills the system
					sys.exit(0)

				else:
					# TODO: maybe we check for users pressing cancel here?
					pass



			else:

				e = exclusions.exclusions(THECONFIG)
				try:
					# if we should shutdown
					if not(e.is_excluded()):

						# now we warn users of impending shutdown
						misc.do_broadcast('DO_WARN()')
						warned = datetime.datetime.today()

						# sleep less often (to see if someone will tap a mouse)
						# but also make sure that we wake up in time before countdown is up
						sleep = min(COUNTDOWN, FASTSLEEP)

					else:
						pass
						# fix the sleep value back to normal-ness
						#sleep = SLEEPTIME


				except SyntaxError, e:
					# FIXME: improve the config parser checker code
					raise SyntaxError, 'syntax error in config file: %s' % e
					sys.exit(1)

				e = None	# free memory



		else:	# not idle

			# datetime objects should return true
			if warned:
				# shutdown was canceled, computer no longer idle
				warned = False
				misc.do_broadcast('DO_SHUTDOWN_CANCELED_MESSAGE()')

			else:
				pass
				# if we want to get rid of idle users even though the entire machine isn't idle
				# TODO:
				#DO: if i.ls_idle(tick=False) ...
				#STILL NEED TO CHECK EXCLUSIONS, AND HAVE SOME SORT OF POLICY ON IF THEY APPLY.
				#MAYBE RUN A SECOND EXCLUSION LOG FILE LIKE: E2.yaml.conf including policies for idle users.



			# sleep just long enough for someone to go idle
			m = i.max_idle(tick=False)
			diff = IDLELIMIT - m
			if diff < SLEEPTIME:
				sleep = diff + 1
			else:
				sleep = SLEEPTIME

		i = None	# free memory

		# catch a signal here and wake up prematurely if we were poked by something.

		# easy sleep
		#time.sleep(math.ceil(sleep))


		# TODO: use select if we can wait for some FD giving us client information...
		# select.select(some_fd_saying_if_someone_pressed_a_button)


		# this block sleeps nicely and catches signals too...


		# TODO: two signals:
		# 1) POKE to get code to loop and re-read config file (eg, from an admin)
		# 2) SHHH (a signal from a user saying hey, i pressed cancel) -> our program can send this if they click a cancel button



		# allow/handle incoming signals
		caught = False
		signal.signal(signal.SIGUSR1, sigusr1)	# handle
		signal.signal(signal.SIGUSR2, sigusr2)	# handle

		def handler(signum, frame):
			"""internal sleep handler function"""
			raise KeyboardInterrupt

		signal.signal(signal.SIGALRM, handler)
		signal.alarm(math.ceil(sleep))

		try:
			signal.pause()
			# pause exited, so a signal was caught
			caught = True
		except KeyboardInterrupt:
			# exception happened, so alarm caused this
			caught = False


		# we continue...
		signal.alarm(0)		# disable the alarm
		signal.signal(signal.SIGUSR1, signal.SIG_IGN)	# ignore
		signal.signal(signal.SIGUSR2, signal.SIG_IGN)	# ignore




def sigusr1():
	pass


def sigusr2():
	pass

if __name__ == "__main__":

	# read: $ man 7 signal
	signal.signal(signal.SIGUSR1, signal.SIG_IGN)	# ignore
	signal.signal(signal.SIGUSR2, signal.SIG_IGN)	# ignore

	# everyone uses this format
	#logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)
	formatter = logging.Formatter(LOGFORMAT)

	# handler for local disk
	RotatingFileHandler = logging.handlers.RotatingFileHandler(MYLOGPATH, maxBytes=1024*100, backupCount=9)
	RotatingFileHandler.setFormatter(formatter)

	# handler for global logging server
	SysLogHandler = logging.handlers.SysLogHandler(LOGSERVER)	# TODO: add a facility as a parameter here
	SysLogHandler.setFormatter(formatter)

	# name a log route, set a level, add handlers
	l = logging.getLogger('evanescent')
	if DEBUGMODE: l.setLevel(logging.DEBUG)
	else: l.setLevel(logging.WARN)
	l.addHandler(RotatingFileHandler)
	l.addHandler(SysLogHandler)

	# handlers in x propagate down to everyone (y) in the x.y tree
	daemon_logger = logging.getLogger('evanescent.daemon')
	other_logger = logging.getLogger('evanescent.other')

	l.info('evanescent says hi')	# send a hello message

	daemon_logger.info('hi from daemon')	# send a hello message
	#other_logger.info('hi from other')	# send a hello message

	d = daemon.daemon(pidfile=DAEMONPID, start_func=evanescent, logger=daemon_logger, close_fds=not(DEBUGMODE))
	d.startstop()

