#!/usr/bin/python
"""
References:
	1.7 How do I get my program to act like a daemon?
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		http://web.archive.org/web/20070410070022/http://www.erlenstar.demon.co.uk/unix/faq_2.html
	do the UNIX double-fork magic, see Stevens'
		"Advanced Programming in the Unix Environment"
		W. Richard Stevens, 1992, Addison-Wesley, ISBN 0-201-56317-7.

A daemon process is usually defined as a background process that does not belong to a terminal session. Many system services are performed by daemons; network services, printing etc.

Simply invoking a program in the background isn't really adequate for these long-running programs; that does not correctly detach the process from the terminal session that started it. Also, the conventional way of starting daemons is simply to issue the command manually or from an rc script; the daemon is expected to put itself into the background.

Here are the steps to become a daemon:

	1. fork() so the parent can exit, this returns control to the command line or shell invoking your program. This step is required so that the new process is guaranteed not to be a process group leader. The next step, setsid(), fails if you're a process group leader.
	2. setsid() to become a process group and session group leader. Since a controlling terminal is associated with a session, and this new session has not yet acquired a controlling terminal our process now has no controlling terminal, which is a Good Thing for daemons.
	3. fork() again so the parent, (the session group leader), can exit. This means that we, as a non-session group leader, can never regain a controlling terminal.
	4. chdir("/") to ensure that our process doesn't keep any directory in use. Failure to do this could make it so that an administrator couldn't unmount a filesystem, because it was our current directory. [Equivalently, we could change to any directory containing files important to the daemon's operation.]
	5. umask(0) so that we have complete control over the permissions of anything we write. We don't know what umask we may have inherited. [This step is optional]
	6. close() fds 0, 1, and 2. This releases the standard in, out, and error we inherited from our parent process. We have no way of knowing where these fds might have been redirected to. Note that many daemons use sysconf() to determine the limit _SC_OPEN_MAX. _SC_OPEN_MAX tells you the maximun open files/process. Then in a loop, the daemon can close all possible file descriptors. You have to decide if you need to do this or not. If you think that there might be file-descriptors open you should close them, since there's a limit on number of concurrent file descriptors.
	7. Establish new open descriptors for stdin, stdout and stderr. Even if you don't plan to use them, it is still a good idea to have them open. The precise handling of these is a matter of taste; if you have a logfile, for example, you might wish to open it as stdout or stderr, and open `/dev/null' as stdin; alternatively, you could open `/dev/console' as stderr and/or stdout, and `/dev/null' as stdin, or any other combination that makes sense for your particular daemon.

Almost none of this is necessary (or advisable) if your daemon is being started by inetd. In that case, stdin, stdout and stderr are all set up for you to refer to the network connection, and the fork()s and session manipulation should not be done (to avoid confusing inetd). Only the chdir() and umask() steps remain as useful.
"""


import sys
import os
import time
import signal	# for signal.SIGTERM
import logging	# for syslog support

class daemon:

	def __init__(self, pidfile=None, logfile=None, start_func=None, close_fds=True, logger=None):
		self.format = '%d/%m/%Y %H:%M:%S'

		self.pidfile = pidfile
		self.logfile = logfile
		self.start_func = start_func
		self.close_fds = close_fds
		self.logger = logger


	def daemonize(self):
		"""this does the double fork magic to turn this into a daemon"""

		# do the first fork
		self.log('trying first fork', logging.DEBUG)
		try:
			pid = os.fork()
			if pid > 0: sys.exit(0) # exit first parent
		except OSError, e:
			message = "fork #1 failed: (%d) %s" % (e.errno, e.strerror)
			self.log(message, logging.FATAL)
			sys.stderr.write(message + "\n")
			sys.exit(1)

		# decouple from parent environment
		os.chdir("/")
		os.umask(0)
		os.setsid()

		# do the second fork
		self.log('trying second fork', logging.DEBUG)
		try:
			pid = os.fork()
			if pid > 0: sys.exit(0) # exit second parent
		except OSError, e:
			message = "fork #2 failed: (%d) %s" % (e.errno, e.strerror)
			self.log(message, logging.FATAL)
			sys.stderr.write(message + "\n")
			sys.exit(1)

		# get pid
		pid = os.getpid()
		message = "process %d running" % pid
		self.log(message, logging.INFO)
		sys.stdout.write(message + "\n")

		# truncate file to zero length before writing (the `+' flag)
		if self.pidfile: file(self.pidfile, 'w+').write("%s\n" % str(pid))

		# make sure we clear out the buffers
		sys.stdout.flush()
		sys.stderr.flush()

		# redirect standard file descriptors
		if self.close_fds:
			sys.stdin = open('/dev/null', 'r')
			sys.stdout = open('/dev/null', 'w')
			sys.stderr = open('/dev/null', 'w')


	def startstop(self, argv=None):
		if argv == None:
			argv = sys.argv

		if len(argv) > 1:
			# what is the action ?
			action = argv[1]

			# look for a pid file
			pid = None
			try:
				pf = None
				pf = file(self.pidfile, 'r')
				pid = int(pf.read().strip())
			except IOError:
				pass
			except ValueError: # happens when we do int('')
				pass
			finally:
				try: pf.close()
				except: pass
				pf = None

			# do the action actions
			if action in ['stop', 'restart']:
				if not pid:
					message = "could not stop, pid file `%s' is missing" % self.pidfile
					sys.stderr.write(message + "\n")
					self.log(message, logging.ERROR)
					sys.exit(1)
				else:

					try:
						# tries to kill whatever has that pid
						os.remove(self.pidfile)
						os.kill(pid, signal.SIGTERM)
						message = "process %d stopped" % pid
						self.log(message, logging.INFO)
						sys.stdout.write(message + "\n")


					except OSError, err:
						err = str(err)
						if err.find("No such process") > 0:

							message = "process not running, pid file removed."
							self.log(message, logging.ERROR)
							sys.stderr.write(message + "\n")
							sys.exit(1)

						else:
							message = "problem stopping error: %s" % err
							self.log(message, logging.CRITICAL)
							sys.stderr.write(message + "\n")
							sys.exit(1)


					if action == 'stop':
						sys.exit(0)

					elif action == 'restart':
						# now setup to do the start below...
						action = 'start'
						pid = None


			# do a start from here, or a [re]start from above.
			if action == 'start':
				if pid:
					message = "start aborted since pid file `%s' exists" % self.pidfile
					self.log(message, logging.ERROR)
					sys.stderr.write(message + "\n")
					sys.exit(1)

				# start it...
				self.log('running daemonize', logging.INFO)
				self.daemonize()
				# run the daemon function
				self.log('running start function', logging.INFO)
				self.start_func()
				return

		else:
			sys.stderr.write("usage: %s start|stop|restart\n" % argv[0])
			sys.exit(1)



	def log(self, message, level=None):
		"""
		simple logging function
		"""
		# are we using the python library for logging, or our own
		if isinstance(self.logger, logging.Logger) or isinstance(self.logger, logging.RootLogger):
			if level == None: self.logger.error(message)	# pick some default level here (we chose 'error')
			else: self.logger.log(level, message)

		elif self.logfile:
			try:
				l = None
				l = open(self.logfile, 'a') # append
				l.write('%s: %s\n' % (time.strftime(self.format), str(message)))
			except IOError:
				pass
			finally:
				try: l.close()
				except: pass
				l = None
		else:
			pass	# no logging enabled

