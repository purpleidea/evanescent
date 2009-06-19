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
################################################################################

# FIXME/TODO: go through all the files and fix all the FIXME's and do all the TODO's
# TODO: check if LOCAL7 facility works on LOGMASTER
# TODO: clean up info/debug messages and make them more sensible/informative
# TODO: have script fail on startup if all the necessary modules aren't installed (ex: python-utmp, yaml)
# TODO: add a big try/except around the main script if possible to catch and log hidden script errors
# TODO: pull in configuration file values from a remote file using wget or curl or similar (idea from rgws@cs.mcgill.ca)
# TODO: check that the license one liner program description is correct at the top of each file.
# TODO: make an evanescent error class, and create specific errors for all the random evanescent things.
# TODO: instead of always logging to dialog, log things into better categories. daemon stuff always goes there, etc...
# TODO: clean up all message strings and add %s data within them, and rewrite them to be clear and clean.
# TODO: we could add an exclusion option for a particular process or program name. eg if program my_proc.py is running, don't shutdown.

# TODO: read some fd with select or listen for some signal that fires on a user logout event
# check online to see if the logout command broadcasts something ?
# we could select() on the utmp file and wake up everytime it changes
# we could get the /etc/gdm/PostSession script to run a kill -USR2 signal to poke this program
# we could select() on the /var/log/auth log file to check for sshd session closed events
# there are pam session events that get triggered. look into pam session for more info.

import os					# for posix/nt detection
import sys					# for sys.exit()
import logging, logging.handlers		# for syslog stuff
import gobject					# for mainloop
import errno					# for standard errno system symbols
import evanescent.daemon as daemon		# i wrote this one
import evanescent.config as config		# i wrote this one
import evanescent.logout.logout as logout	# logout in logout package
import evanescent.logout.users as users		# users in logout package
import evanescent.exclusions as exclusions	# exclusions module
import evanescent.misc as misc			# miscellaneous such as uptime

class evanescent_daemon:

	# CONSTRUCTOR #########################################################
	def __init__(self, name=None, start=None):
		"""constructor for the evanescent_daemon class."""

		# MISC ########################################################
		self.name = 'evanescent'

		# LOGGING #####################################################
		self.log = None	# main logger
		self.logh = {}	# log handles
		self.logs = {}	# other log handles

		# setup the logging handles
		self.logging()

		# GOBJECT #####################################################
		self.mainloop = None		# mainloop object
		self.source_id = None		# timer id


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
		self.logh['SysLogHandler'] = logging.handlers.SysLogHandler(tuple(config.LOGSERVER), logging.handlers.SysLogHandler.LOG_LOCAL7)
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
		self.logs['daemon'] = logging.getLogger('%s.daemon' % self.name)
		self.logs['dialog'] = logging.getLogger('%s.dialog' % self.name)
		#self.logs['signal'] = logging.getLogger('%s.signal' % self.name)
		#self.logs['evalog'] = logging.getLogger('%s.evalog' % self.name)

		# send a hello message
		self.log.debug('hello from %s' % self.name)


	# MAIN ################################################################
	def main(self):
		"""main to run for the class."""

		# should evanescent be disabled, and exit right away?
		if not(config.STARTMEUP): sys.exit()

		# create the mainloop object
		# http://www.pygtk.org/docs/pygobject/class-gobjectmainloop.html
		self.mainloop = gobject.MainLoop()

		# start off our initial event source in one second from now.
		self.source_id = gobject.timeout_add(1*1000, self.loop)

		# create daemon object
		if os.name == 'posix':
			d = daemon.daemon(pidfile=config.DAEMONPID, start_func=self.mainloop.run, logger=self.logs['daemon'], close_fds=not(config.DEBUGMODE))

		try:
			if os.name == 'posix': d.start_stop()
			elif os.name == 'nt': self.mainloop.run()
			else: raise AssertionError('os: `%s\' is not supported at this time.' % os.name)

		except KeyboardInterrupt, e:
			if os.name == 'posix':
				d.start_stop([sys.argv[0], 'stop'])
			elif os.name == 'nt':
				self.mainloop.run()

		except SystemExit:
			pass

		except:
			# special logfile for if something bad happens
			import traceback
			self.log.fatal('fatal exception:\n%s' % traceback.format_exc())
			try:
				traceback.print_exc(file=open(config.MYERRPATH, 'w+'))

			except IOError, e:
				# we don't have permission to write the MYERRPATH log file.
				# 'Permission denied'
				if e.errno == errno.EACCES:
					pass


	# WORKING LOOP ########################################################
	def loop(self):
		"""this is the main loop for evanescent_daemon."""

		self.logs['dialog'].debug('entering local loop()')
		sleep = config.SLEEPTIME

		# from the time when a machine comes up, give users a chance of
		# `INITSLEEP' seconds to login before the empty machine is
		# considered idle and shuts itself down. idea for this feature
		# from: andrewb@cs.mcgill.ca
		uptime = misc.uptime()
		self.logs['dialog'].debug('uptime is: %d' % uptime)
		if config.INITSLEEP > 0 and uptime < config.INITSLEEP:
			self.logs['dialog'].debug('machine just booted, excluding from shutdown')
			sleep = config.INITSLEEP - uptime

		# check for users on the machine
		elif not users.exist():
			self.logs['dialog'].warn('no users are present.')

			e = exclusions.exclusions(yamlconf=config.THECONFIG)
			# do the check, and if it passes get the good value.
			result = e.is_fileok()
			if result: result = e.is_excluded()
			# otherwise it's false anyways! not excluded!
			else:
				self.logs['dialog'].warn('problem with config file.')
				self.log.warn('assuming no exclusions.')

			e = None			# clean up the object

			# if not excluded
			if not result:
				self.log.warn('you are currently NOT excluded from idle-logout.')

				self.log.fatal('machine is being shutdown due to inactivity.')
				# do the actual shutdown
				logout.shutdown()
				self.mainloop.quit()
				return False

		sleep = max(1, sleep)		# sleep for at least one second
		self.log.info('going to sleep for %d seconds.' % sleep)

		# add a new timeout so this gets called again
		self.source_id = gobject.timeout_add(sleep*1000, self.loop)

		# this loop ends, and we wait for the above rescheduled event
		return False


if __name__ == '__main__':

	e = evanescent_daemon()
	e.main()

