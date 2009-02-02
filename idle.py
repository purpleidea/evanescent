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

import os		# for stat (to get idle times)
import time		# for the idle time math
import math		# need this for math.floor for windows
if os.name in ['posix']:
	import utmp		# lib to read the utmp file
	import UTMPCONST



class idle:
	"""gives information about idling login sessions
	the system has `tick' parameters to allow us running
	multiple queries (eg: unique_users, ls_idle, etc...)
	without worrying about """

	def __init__(self, tick_default=False, me=True):
		self.__result = None			# saved result from __idle
		self.tick_default = tick_default	# default value for tick
		self.me = me				# used by __widle() for nt only
		self.tick(True)				# tick once

	def is_idle(self, threshold=0, tick=None):
		"""returns whether the entire machine is idle or not"""
		self.tick(tick)
		result = self.__result
		return (len(self.active_indices(threshold=threshold, tick=tick)) == 0)

	def max_idle(self, tick=None):
		"""returns the longest duration someone has been idle for"""
		self.tick(tick)
		result = self.__result
		return result['max']

	def min_idle(self, tick=None):
		"""returns the shortest duration someone has been idle for"""
		self.tick(tick)
		result = self.__result
		return result['min']

	def get_idle(self, index, tick=None):
		"""get idle time for particular index, as returned by idle_indices
		returns an array of idle times if we give an array of indices"""
		self.tick(tick)
		if type(index) == type([]):
			a = []
			for x in index:
				temp = self.get_idle(x)
				# add as long as we don't have a boolean type
				# (which could only to be a False value)
				if not(type(temp) == type(False)): a.append(temp)
			return a
		else:
			try:
				return self.__result['idle'][index]
			except IndexError:
				return False

	def get_line(self, index, tick=None):
		"""get line for particular index, as returned by idle_indices
		returns an array of lines if we give an array of indices"""
		self.tick(tick)
		if type(index) == type([]):
			a = []
			for x in index:
				temp = self.get_line(x)
				if not(type(temp) == type(False)): a.append(temp)
			return a
		else:
			try:
				return self.__result['line'][index]
			except IndexError:
				return False

	def get_user(self, index, tick=None):
		"""get user for particular index, as returned by idle_indices
		returns an array of users if we give an array of indices"""
		self.tick(tick)
		if type(index) == type([]):
			a = []
			for x in index:
				temp = self.get_user(x)
				if not(type(temp) == type(False)): a.append(temp)
			return a
		else:
			try:
				return self.__result['users'][index]
			except IndexError:
				return False

	def idle_indices(self, threshold=0, tick=None, reverse=False):
		"""returns a list of indices corresponding to which users are idle past a threshold"""
		self.tick(tick)
		a = []
		z = []
		i = 0
		for x in self.__result['idle']:
			if x >= threshold: a.append(i)
			else: z.append(i)
			i = i + 1

		if not(reverse): return a
		else: return z

	def active_indices(self, threshold=0, tick=None):
		"""returns a list of indices corresponding to which users aren't idle past a threshold"""
		return self.idle_indices(threshold=threshold, tick=tick, reverse=True)

	def ls_users(self, tick=None):
		"""returns a list of users logged in-- duplicates for multiple logins"""
		self.tick(tick)
		result = self.__result
		return result['users']

	def unique_users(self, tick=None):
		"""returns a unique (no duplicates) list of logged in users"""
		return list(set(self.ls_users(tick)))

	def tick(self, do_tick=None):
		"""tries to update the idle cache.
		does so if do_tick is true. if it's None, then does the default."""
		if do_tick == None:	# then do the default
			do_tick = self.tick_default
		if do_tick: self.__result = self.__idle()

	def idle(self, tick=None):
		"""runs a fresh idle call and returns it"""
		result = self.__idle()
		if tick: self.__result = result
		return self.__result


	def __idle(self):
		"""private function that does all the work"""

		if os.name in ['nt']: return self.__widle()

		#f = "%-10s %-5s %10s %-10s %-25s %-15s %-10s %-10s %-10s %-10s %-10s"
		#print f % ("USER", "TTY", "PID", "HOST", "LOGIN", "IDLE", "TYPE", "SESSION", "ID", "EXIT", "IPV6")
		#print f % (x.ut_user, x.ut_line, x.ut_pid, x.ut_host, time.ctime(x.ut_tv[0]), z, x.ut_type, x.ut_session, x.ut_id, x.ut_exit, x.ut_addr_v6)

		a = []			# a is for array
		# d is for dictionary
		d = {'idle': [], 'users': [], 'line': [], 'max': None, 'min': None, 'len': 0}
		u = utmp.UtmpRecord()	# (iterator)
		for x in u:		# u is for utmp
			if x.ut_type == UTMPCONST.USER_PROCESS:

				z = None
				try:	# try/except in case /dev/* doesn't work/exist
					tty_stat = os.stat("/dev/" + x.ut_line)
					z = time.time() - tty_stat.st_atime
				except:
					z = None

				if d['max'] == None: d['max'] = z
				if d['min'] == None: d['min'] = z
				d['max'] = max(d['max'], z)	# set the new max
				d['min'] = min(d['min'], z)	# set the new min

				d['idle'].append(z)
				d['users'].append(x.ut_user)
				d['line'].append(x.ut_line)
				d['len'] = d['len'] + 1

		u.endutent()	# closes the utmp file

		# returns a dictionary of data;
		# key: `idle' is a list of idle times
		# key: `users' is a list of users logged on. (duplicates may occur!)

		return d


	def __widle(self):
		"""windows version of the private __idle function.
		if me is True, return widle of just the current user.
		if me is False, return widle of every user that
		broadcast text file idle data to us. if me is None,
		then return widle data from both of those. Choosing
		which of these are good ideas is up to you!"""
		import locale
		import getpass

		d = {'idle': [], 'users': [], 'line': [], 'max': None, 'min': None, 'len': 0}

		# get the data from the current user
		if (self.me is None) or self.me:
			o = os.popen('widle.bat', 'r')		# run our script
			a = o.readlines()			# grab all the output
			o.close()
			o = None
			for i in range(len(a)):			# loop
				if a[i].startswith('WIDLE'):	# find magic identifier
					if i+1 < len(a):	# does the next index exist?
						z = int(math.floor(locale.atoi(a[i+1])/1000))

						if d['max'] == None: d['max'] = z
						if d['min'] == None: d['min'] = z
						d['max'] = max(d['max'], z)	# set the new max
						d['min'] = min(d['min'], z)	# set the new min

						d['idle'].append(z)
						d['users'].append(getpass.getuser())	# i guess this is how i could get the login
						d['line'].append('FIXME?')		# FIXME: put something useful/meaningful?
						d['len'] = d['len'] + 1
						break

		# get the data from any clients broadcasting
		if (self.me is None) or not(self.me):
			clients = os.listdir( os.path.join(config.SHAREDDIR, self.IDLEDIR) )
			t = time.time()
			for i in range(len(clients)):
				# get the data from that particular client
				g = yamlhelp.yamlhelp(os.path.join(config.SHAREDDIR, self.IDLEDIR, i))
				data = g.get_yaml()
				# when we grab from a file, we only every expect one element.
				if len(data['users']) > 1: raise AssertionError('only expected one user')

				# the current idle time for a user is:
				# the sum of the idle time reported at
				# a specific time in the past, and the
				# time difference between that reading
				# and the current time now. the offset
				# addition is probably a fair estimate
				# since idle data from clients is read
				# fairly often and any time errors are
				# insignificant, with respect to total
				# timeout times for the inactive user.
				z = data['widle']['idle'][0] + ( t - data['tsync'] )

				if d['max'] == None: d['max'] = z
				if d['min'] == None: d['min'] = z
				d['max'] = max(d['max'], z)	# set the new max
				d['min'] = min(d['min'], z)	# set the new min

				d['idle'].append(z)
				d['users'].append( data['widle']['users'][0] )
				d['line'].append( data['widle']['line'][0] )
				d['len'] = d['len'] + 1

		return d

