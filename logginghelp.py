#!/usr/bin/python
"""
    Logginghelp wrapper to simplify implementation of message logging for me.
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

import os
import logging
import logging.handlers

DEFAULT_PATH = None

class logginghelp:

	def __init__(self,
		name, wordymode=True, mylogpath=[DEFAULT_PATH], logserver=None,
		logformat='%(asctime)s %(levelname)-8s %(name)-17s %(message)s',
		hello=False):
		"""this class is meant to ease the use of the python logging
		class. the code assumes some sensible defaults, and if you want
		something different, then this class can probably be easily
		changed to support the feature or parameter that you want."""

		# some variables
		self.name = name			# a name for this log
		self.wordymode = bool(wordymode)	# extra speak
		self.mylogpath = mylogpath		# array of rotating logs
		self.logserver = logserver		# for remote syslog
		self.logformat = logformat		# the format for all

		# add os specific default path to the processing
		if os.name == 'nt': path = 'c:\WINDOWS\system32\config\%s.log'
		elif os.name == 'posix': path = '/var/log/%s.log'
		# if the True value is found in log path, then do a default log
		if DEFAULT_PATH in self.mylogpath:
			while DEFAULT_PATH in self.mylogpath:
				self.mylogpath.remove(DEFAULT_PATH)
			# add a log file at the default location for os
			self.mylogpath.append(path % self.name)

		# log objects
		self.log = None			# main logger
		self.logh = {}			# log handles
		self.logs = {}			# other log handles

		# do the logging init
		self.__logging()

		# send a hello message
		if hello: self.log.debug('hello from: %s' % self.name)


	def __logging(self):
		"""setup logging. this function doesn't return any value."""
		# error logging levels:
		#	* CRITICAL
		#	* FATAL
		#	* ERROR
		#	* WARN
		#	* INFO
		#	* DEBUG

		# have every log use this format
		formatter = logging.Formatter(self.logformat)

		# name a log route & set a level
		self.log = logging.getLogger(self.name)
		if self.wordymode: self.log.setLevel(logging.DEBUG)
		else: self.log.setLevel(logging.WARN)

		# handler for stderr
		self.logh['StreamHandler'] = logging.StreamHandler()
		self.logh['StreamHandler'].setFormatter(formatter)
		self.log.addHandler(self.logh['StreamHandler'])
		del self.logh['StreamHandler']

		# handler for global logging server
		if self.logserver is not None:
			# TODO: is there a way to change the facility to a
			# specific name?
			self.logh['SysLogHandler'] = \
			logging.handlers.SysLogHandler(
				tuple(self.logserver),
				logging.handlers.SysLogHandler.LOG_LOCAL7
			)
			self.logh['SysLogHandler'].setFormatter(formatter)
			self.log.addHandler(self.logh['SysLogHandler'])
			del self.logh['SysLogHandler']

		# handler for windows event log
		if os.name == 'nt':
			self.logh['NTEventLogHandler'] = \
			logging.handlers.NTEventLogHandler(self.name)
			self.logh['NTEventLogHandler'].setFormatter(formatter)
			self.log.addHandler(self.logh['NTEventLogHandler'])
			del self.logh['NTEventLogHandler']

		# handlers for local disk
		# NOTE: using access() to check if a user is authorized to e.g.
		# open a file before actually doing so using open() creates a
		# security hole, because the user might exploit the short time
		# interval between checking and opening the file to manipulate
		# it. do a try and catch instead.
		for x in self.mylogpath:
			try:
				self.logh['RotatingFileHandler'] = \
				logging.handlers.RotatingFileHandler(
					x,
					maxBytes=1024*100,
					backupCount=9
				)
				self.logh['RotatingFileHandler'].setFormatter(formatter)
				self.log.addHandler(self.logh['RotatingFileHandler'])

			except IOError:
				# you probably don't have the file permissions
				# to open the file. you probably need root.
				self.log.warn('unable to open `%s\' for use as a log file.' % x)

			finally:
				if 'RotatingFileHandler' in self.logh:
					del self.logh['RotatingFileHandler']


	def get_log(self, name=None):
		"""return a handle to the main logger or optionally to
		an additional handler should you specify the name. if
		the additional handler doesn't exist, then it will be
		created."""

		if name is None:
			return self.log

		elif name in self.logs:
			return self.logs[name]

		else:
			# handlers in x propagate down to everyone (y)
			# in the x.y tree
			self.logs[name] = \
			logging.getLogger('%s.%s' % (self.name, name))
			return self.logs[name]


if __name__ == '__main__':
	import sys
	obj = logginghelp(__name__, hello=True)
	log = obj.get_log()
	log.info('argv: %s' % ', '.join(sys.argv))

