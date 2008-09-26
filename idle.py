#!/usr/bin/python

import utmp		# lib to read the utmp file
import UTMPCONST
import os		# for stat (to get idle times)
import time		# for the idle time math



class idle:
	"""gives information about idling login sessions
	the system has `tick' parameters to allow us running
	multiple queries (eg: unique_users, ls_idle, etc...)
	without worrying about """

	def __init__(self, tick_default=False):
		self.__result = None			# saved result from __idle
		self.tick_default = tick_default	# default value for tick
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
				if temp: a.append(temp)
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
				if temp: a.append(temp)
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
				if temp: a.append(temp)
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


