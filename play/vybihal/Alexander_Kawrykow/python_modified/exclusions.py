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

#ASSIGNMENT 5
import urllib2                          #for pulling remote conf file

import random				#A5 add on... for choosing a radom number



# TODO: rework this exclusions file to use the yamlhelp wrapper functions i've made...
import yaml				# yaml for config file parsing
import fnmatch				# for simple shell-style pattern matching
import socket				# for gethostname() and getfqdn()
import os				# for getlogin(), geteuid() and getegid()
import dt				# i wrote this one-- for time/date range parsing
if os.name in ['posix']: import pwd	# for unix passwd file lookup
else: import getpass			# to find the username

# constants
HOST = 'host'
FQDN = 'fqdn'
TIME = 'time'

# these use the `users' parameter for is_excluded()
USER = 'user'
EUID = 'euid'
EGID = 'egid'

# TODO: (not yet implemented)
DATE = 'date'
IPV4 = 'ipv4'
IPV6 = 'ipv6'
MACA = 'maca'	# mac address

# special
CONF = 'conf'	# for config options
NOTE = 'note'	# for adding comments



# ASSIGNMENT 5 add on: will randomly select a computer for shutdown based on their pid
PID = 'pid'




class exclusions:

	def __init__(self, yamlconf, time_shift=0, case=False):
		"""most of the params, aren't case specific, so
		decide if we should match them as such or not.
		case == True: case sensitive matching
		case == False: case insensitive matching
		"""
		self.yamlconf = yamlconf
		self.time_shift = int(time_shift)	# do date/time calculations assuming shift of delta seconds
		self.case = case

	def syntax_ok(self, message=False):
		# TODO: in the future, we could run some specific parser script to check syntax
		# the easy way is to see if it actually fails when we run it...
		# the problem is that the is_excluded exits early when it knows it can, and sometimes
		# not all the picky syntax has been checked yet...
		"""is the config file properly formatted"""
		try:
			self.is_excluded()
		except SyntaxError, strerror:
			if message: return "SyntaxError: %s" % strerror
			else: return False

		return True

	def is_excluded(self, users=[]):
		"""returns True if there should be an exclusion to
		shutdown the machine for a particular static (from
		config file) reason. If you specify a username, then
		it will do the exclusions based on _that_ user name
		instead of based on the user running the script (root,
		usually-- which we don't care about) so this it is a
		good thing to use this with a username. if you specify
		a list of usernames then it will try to exclude the
		machine on any rule trying all usernames.
		"""

		# array of users at least one long
		if (type(users) == type([])) and (len(users) > 0):
			for x in users:
				temp = self.is_excluded(x)
				# if it's excluded for this user, then it's
				#excluded for the machine of course.
				if temp:
					return True

			return False	# didn't exclude anyone.

		# username with at least one character
		elif (type(users) == type('')) and len(users) > 0:

			user = users
			try:
				if not(os.name in ['posix']): raise KeyError
				temp = pwd.getpwnam(users)
				if users != temp[0]: raise AssertionError
				euid = temp[2]	# pw_uid
				egid = temp[3]	# pw_gid
			except KeyError:
				euid = False
				egid = False

		# old school, normal(bad) is_excluded() operation
		else:
			if os.name in ['posix']:
				# use the info from the user running the script
				try:
					#NOTE: when this runs with no environment variables it throws an error...
					#OSError: [Errno 2] No such file or directory
					user = os.getlogin()
				except OSError:
					#user = root
					user = pwd.getpwuid(os.getuid())[0]
				euid = os.geteuid()
				egid = os.getegid()
			else:
				user = getpass.getuser()
				euid = False
				egid = False

		shutdown = True		# shutdown machines by default

		try:

			#!! ORIGINAL - local file:
                        #f = None
                        #f = open(self.yamlconf)i

                        #!! ASSIGNMENT 5 FILE MODIFIED - remote file:

                        f=urllib2.urlopen('http://www.cs.mcgill.ca/~plevin2/evanescent.conf.yaml.example')

			try:
				data = yaml.load(f)
				if type(data) != type([]):
					raise SyntaxError, 'top level yaml config struct should be an array'

				# loop through each set in the conf file
				for i in data:
					row = False
					# loop through each key in the dictionary
					for j in i.keys():

						# hostname
						if j == HOST:
							# uses: socket.gethostname()
							if not(fnmatch.fnmatchcase(self.c(socket.gethostname()), self.c(i[j]))):
							#if socket.gethostname() != i['host']: # simple matching
								row = False
								break
							else: row = True

						# fqdn, falls back to hostname if not available
						elif j == FQDN:
							# uses: socket.getfqdn()
							if not(fnmatch.fnmatchcase(self.c(socket.getfqdn()), self.c(i[j]))):
								row = False
								break
							else: row = True

						#*** login (luser) name
						elif j == USER:
							# uses: os.getlogin()
							if not(fnmatch.fnmatchcase(self.c(user), self.c(i[j]))):
								row = False
								break
							else: row = True

						#*** effective user id
						elif j == EUID and os.name in ['posix']:
							# uses: os.geteuid()
							if not(fnmatch.fnmatchcase(self.c(euid), self.c(i[j]))):
								row = False
								break
							else: row = True

						#*** effective group id
						elif j == EGID and os.name in ['posix']:
							# uses: os.getegid()
							if not(fnmatch.fnmatchcase(self.c(egid), self.c(i[j]))):
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
							# A5 ADD ON 
                                                        #Also uses the dt module
                                                        temp = dt.dt(time_shift=self.time_shift)
                                                        if not( temp.is_date(i[j])):
                                                                row = False
                                                                break
                                                        else: row = True
							
						#A5 add on...
						elif j == PID:
						#a random number is used to decide if the computer should be shut down or not
							temp_num = random.randint(1, 1000)
                                                        if i[j] > temp_num:
                                                                row = False
								break
                                                        else: row = True



						elif j == NOTE:
							# the exclusions function should ignore any comments.
							pass

						elif j == CONF:
							# the exclusions function should ignore configuration file options
							pass
						else:
							raise SyntaxError, "identifier `%s' not supported" % j

					# if we have a valid row, then the exclusion should happen since the rows are OR-ed together
					if row:
						shutdown = False
						break

			# add any other parsing errors we find here...
			except SyntaxError, e:
				raise SyntaxError, "parsing error: %s" % e

			except yaml.scanner.ScannerError, e:
				raise SyntaxError, "parsing error: %s" % e

		except IOError:
			pass

		finally:
			try: f.close()
			except: pass
			f = None

		return not(shutdown)

	def c(self, x):
		"""
		case == True: case sensitive matching
		case == False: case insensitive matching
		"""
		x = str(x)
		if self.case: return x
		else: return x.upper()


