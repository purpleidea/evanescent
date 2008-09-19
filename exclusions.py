#!/usr/bin/python


import yaml		# yaml for config file parsing
import fnmatch		# for simple shell-style pattern matching
import socket		# for gethostname() and getfqdn()
import os		# for getlogin(), geteuid() and getegid()
import dt		# i wrote this one-- for time/date range parsing


# constants
HOST = 'host'
FQDN = 'fqdn'
USER = 'user'
EUID = 'euid'
EGID = 'egid'
TIME = 'time'

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
		# FIXME: in the future, we could run some specific parser script to check syntax
		# the easy way is to see if it actually fails when we run it...
		# the problem is that the is_excluded exits early when it knows it can, and sometimes
		# not all the picky syntax has been checked yet...
		"""is the config file properly formatted"""
		try:
			self.is_excluded()
		except SyntaxError:
			return False

		return True

	def is_excluded(self):
		"""returns True if there should be an exclusion
		to shutdown the machine for a particular static
		(from config file) reason."""
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
							if not(fnmatch.fnmatchcase(self.c(os.getlogin()), self.c(i[j]))):
								row = False
								break
							else: row = True

						#*** effective user id
						elif j == EUID:
							# uses: os.geteuid()
							if not(fnmatch.fnmatchcase(self.c(os.geteuid()), self.c(i[j]))):
								row = False
								break
							else: row = True

						#*** effective group id
						elif j == EGID:
							# uses: os.getegid()
							if not(fnmatch.fnmatchcase(self.c(os.geteuid()), self.c(i[j]))):
								row = False
								break
							else: row = True


						elif j == TIME:
							# uses: dt module that i wrote
							# TODO: does this need to be enclosed in a try/catch (because it can raise?)
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


