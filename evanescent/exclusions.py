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

# TODO: rework this exclusions file to use the yamlhelp wrapper functions
import yaml		# yaml for config file parsing
import fnmatch		# for simple shell-style pattern matching
import socket		# for gethostname() and getfqdn()
import getpass		# for getuser()
import os		# for geteuid() and getegid()
import errno		# for standard errno system symbols
import dt		# i wrote this one-- for time/date range parsing

# constants
HOST = 'host'
FQDN = 'fqdn'
TIME = 'time'
USER = 'user'
EUID = 'euid'
EGID = 'egid'

# TODO: (not yet implemented)
DATE = 'date'
IPV4 = 'ipv4'
IPV6 = 'ipv6'
MACA = 'maca'		# mac address

# special
CONF = 'conf'		# for config options
NOTE = 'note'		# for adding comments

class exclusions:

	# TODO: translate these
	E_NOTALIST = 'top level yaml exclusions file struct should be a list'
	E_YAMLSCAN = 'yaml parser failed with: %s'
	E_FILEMISSING = 'file `%s\' doesn\'t exist.'

	def __init__(self, yamlconf, time_shift=0):
		"""the constructor for the exclusions class. some parameters are
		matched in a case-sensitive way, and others case-insensitive."""
		self.yamlconf = os.path.abspath(yamlconf)	# conf file path
		# do date/time calculations assuming shift of delta seconds
		self.time_shift = int(time_shift)		# the time shift


	def __is_excluded(self):
		"""should i be excluded from shutdown?"""
		# TODO: do any of the conditions below need to be enclosed
		# in try/catch blocks? eg: getpass.getuser(), or others ??

		shutdown = True		# shutdown machines unless excluded

		# open yaml file and parse using yaml library.
		try:
			f = None
			f = open(self.yamlconf)
			try:
				data = yaml.load(f)
				if type(data) is not list:
					raise SyntaxError, self.E_NOTALIST

			except yaml.scanner.ScannerError, e:
				raise SyntaxError, self.E_YAMLSCAN % e

		except IOError, e:
			if e.errno == errno.ENOENT:
				raise IOError, self.E_FILEMISSING % self.yamlconf
			else:
				raise IOError, e

		finally:
			try: f.close()
			except: pass
			f = None

		# TODO: we could probably clean up this big loop
		# and replace it with some more elegant code.

		# loop through each set in the conf file
		for i in data:
			row = False
			# loop through each key in the dictionary
			for j in i.keys():

				# hostname
				if j == HOST:
					if self.compare(socket.gethostname(), i[j], sensitive=False):
						row = False
						break
					else: row = True

				# fqdn, falls back to hostname if not available
				elif j == FQDN:
					if self.compare(socket.getfqdn(), i[j], sensitive=False):
						row = False
						break
					else: row = True

				#*** login (luser) name
				elif j == USER:
					if self.compare(getpass.getuser(), i[j], sensitive=True):
						row = False
						break
					else: row = True

				#*** effective user id (unix only!)
				elif j == EUID and os.name == 'posix':
					if self.compare(os.geteuid(), i[j], sensitive=False):
						row = False
						break
					else: row = True

				#*** effective group id (unix only!)
				elif j == EGID and os.name == 'posix':
					if self.compare(os.getegid(), i[j], sensitive=False):
						row = False
						break
					else: row = True

				elif j == TIME:
					# uses: dt module that i wrote
					# TODO: does this need to be enclosed in a try/catch (because it can raise)
					temp = dt.dt(time_shift=self.time_shift)
					if not( temp.is_time(i[j]) ):
						row = False
						break
					else: row = True

				elif j == DATE:
					# TODO...
					pass

				elif j == NOTE:
					# the exclusions function should ignore any comments.
					pass

				elif j == CONF:
					# the exclusions function should ignore configuration file options
					pass
				else:
					raise SyntaxError, 'identifier: `%s\' not supported' % j

			# if we have a valid row, then the exclusion should happen since the rows are OR-ed together
			if row:
				shutdown = False
				break

		return not(shutdown)


	def is_excluded(self, result=False):
		"""this function wraps the main is_excluded() function in a
		try/except, and lets us choose what the result should be if
		there is an error. if result == False, then return False on
		error. if result == True, then return True on error. and if
		result is None, then propagate out the original error."""

		assert type(result) in [type(None), bool]
		try:
			return self.__is_excluded()
		except BaseException, e:
			if result is None:
				raise e
			else: return bool(result)


	def is_fileok(self):
		# TODO: in the future, we could run some specific parser script to check syntax
		# the easy way is to see if it actually fails when we run it...
		# the problem is that the is_excluded exits early when it knows it can, and sometimes
		# not all the picky syntax has been checked yet...
		"""is the .conf file present, parseable & properly formatted?"""
		try:
			self.is_excluded(result=None)
		except:
			# TODO: should we log the specific error ?
			return False

		return True


	def compare(self, a, b, sensitive=True):
		"""compares two strings in the manner most commonly implemented
		by the is_excluded function. this saves retyping code above."""

		return not fnmatch.fnmatchcase(
			self.case(a, sensitive=bool(sensitive)),
			self.case(b, sensitive=bool(sensitive))
		)


	def case(self, string, sensitive=True):
		"""the case function returns the string in either its original
		case if sensitive == True: (case sensitive matching) or in upper
		case if sensitive == False: (case insensitive matching). this is
		a helper function for the main compare function shown above."""
		string = str(string)
		if bool(sensitive): return string
		else: return string.upper()


# allow this module to be run individually and output some diagnostic info.
if __name__ == '__main__':
	import sys
	yamlconf = '/etc/evanescent.conf.yaml'	# the default
	def usage():
		"""print a simple usage message and exit."""
		print 'usage: %s [yamlconf] | [-h | --help]' % sys.argv[0]
		sys.exit(0)

	if len(sys.argv) == 2:
		if sys.argv[1] in ['-h', '--help']:
			usage()
		else:
			yamlconf = sys.argv[1]
	elif len(sys.argv) > 2: usage()

	e = exclusions(yamlconf=yamlconf)
	print 'yamlconf:\t%s' % yamlconf
	print 'is_fileok():\t%s' % e.is_fileok()
	print 'is_excluded():\t%s' % e.is_excluded(result=None)

