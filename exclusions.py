#!/usr/bin/python


import yaml		# yaml for config file parsing
import fnmatch		# for simple shell-style pattern matching
import socket		# for gethostname() and getfqdn()
import os		# for getlogin(), geteuid() and getegid()
import pwd		# for unix passwd file lookup
import dt		# i wrote this one-- for time/date range parsing


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

	def syntax_ok(self):
		# TODO: in the future, we could run some specific parser script to check syntax
		# the easy way is to see if it actually fails when we run it...
		# the problem is that the is_excluded exits early when it knows it can, and sometimes
		# not all the picky syntax has been checked yet...
		"""is the config file properly formatted"""
		try:
			self.is_excluded()
		except SyntaxError:
			return False

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
				temp = pwd.getpwnam(users)
				if users != temp[0]: raise AssertionError
				euid = temp[2]	# pw_uid
				egid = temp[3]	# pw_gid
			except KeyError:
				euid = False
				egid = False

		# old school, normal(bad) is_excluded() operation
		else:
			# use the info from the user running the script
			user = os.getlogin()
			euid = os.geteuid()
			egid = os.getegid()


		shutdown = True		# shutdown machines by default

		try:
			f = None
			f = open(self.yamlconf)
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
						elif j == EUID:
							# uses: os.geteuid()
							if not(fnmatch.fnmatchcase(self.c(euid), self.c(i[j]))):
								row = False
								break
							else: row = True

						#*** effective group id
						elif j == EGID:
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


						elif j == 'date':


							pass

						elif j == 'something...':


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


