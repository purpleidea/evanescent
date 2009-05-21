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
import yamlhelp		# for getting foreign idle times
import config
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
		does so if do_tick is true. if it's
		None, then it does the default."""
		if do_tick == None:	# then do the default
			do_tick = self.tick_default
		if do_tick: self.__result = self.__idle()


	def idle(self, tick=None):
		"""returns the output from a standard
		idle call; with and without tick()"""
		result = self.__idle()
		if tick: self.__result = result
		return self.__result


	def __idle(self):
		"""private function that collaborates the work
		from all the various idle functions calls. this
		is what is typically called when deciding if a
		machine is considered idle or not."""

		#if os.name in ['nt']: return self.__widle()

		# d is for dictionary
		d = {'idle': [], 'users': [], 'line': [], 'max': None, 'min': None, 'len': 0}


		#u = __utmpidle()
		#x = __xssidle()

		#...
		return None

		#return d


	def __xprintidle(self):
		"""return idle time in ms from xprintidle command."""
		import os
		import getpass
		# TODO: add check for xprintidle command being installed.
		result = False
		try:
			o = os.popen('xprintidle', 'r')		# run the program
			a = o.readlines()			# grab all the output
		except:
			pass
		finally:
			o.close()
			o = None

		if len(a) == 1: result = int(a[0].strip())

		# FIXME: find out how to get the line associated with the current X server running the xprintidle
		# NOTE: this should work if the user is calling the script: os.ttyname(sys.stdin)
		if not(result): return {'idle': [], 'users': [], 'line': [], 'max': None, 'min': None, 'len': 0}
		return {'idle': [result], 'users': [getpass.getuser()], 'line': ['?'], 'max': result, 'min': result, 'len': 1}


	def __widle(self):
		"""return windows idle time in ms from widle.bat command."""
		import os
		import math
		import getpass
		result = False
		a = []
		try:
			o = os.popen('widle.bat', 'r')		# run our script
			a = o.readlines()			# grab all the output
		except:
			pass

		finally:
			o.close()
			o = None

		for i in range(len(a)):			# loop
			if a[i].startswith('WIDLE'):	# find magic identifier
				if i+1 < len(a):	# does the next index exist?
					result = int(math.floor(locale.atoi(a[i+1])))
					break

		# FIXME: find out how to get the line associated with the running command (if one even exists)
		if not(result): return {'idle': [], 'users': [], 'line': [], 'max': None, 'min': None, 'len': 0}
		return {'idle': [result], 'users': [getpass.getuser()], 'line': ['?'], 'max': result, 'min': result, 'len': 1}


	def __xssidle(self):
		"""return idle time in ms from X11 xss extensions."""
		# FIXME: this may or may not suffer from the dpms bug.
		import os
		import ctypes
		import getpass

		class XScreenSaverInfo(ctypes.Structure):
			"""typedef struct { ... } XScreenSaverInfo;"""
			_fields_ = [
				('window',      ctypes.c_ulong),	# screen saver window
				('state',       ctypes.c_int),		# off,on,disabled
				('kind',        ctypes.c_int),		# blanked,internal,external
				('since',       ctypes.c_ulong),	# milliseconds
				('idle',        ctypes.c_ulong),	# milliseconds
				('event_mask',  ctypes.c_ulong)		# events
			]

		xlib = ctypes.cdll.LoadLibrary('libX11.so')
		# TODO: can this be modified to query a different Xdisplay?
		# this way it can be run as root in the daemon, and doesn't
		# have to depend on the client running an eva style program
		dpy = xlib.XOpenDisplay(os.environ['DISPLAY'])
		root = xlib.XDefaultRootWindow(dpy)
		xss = ctypes.cdll.LoadLibrary('libXss.so')
		xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
		xss_info = xss.XScreenSaverAllocInfo()
		xss.XScreenSaverQueryInfo(dpy, root, xss_info)

		result = int(xss_info.contents.idle)			# idle time in milliseconds

		# FIXME: find out how to get the line associated with the current X server running on $DISPLAY
		return {'idle': [result], 'users': [getpass.getuser()], 'line': ['?'], 'max': result, 'min': result, 'len': 1}


	def __utmpidle(self):
		"""return idle times in ms from utmp database."""
		import os
		import utmp
		import time

		#f = "%-10s %-5s %10s %-10s %-25s %-15s %-10s %-10s %-10s %-10s %-10s"
		#print f % ("USER", "TTY", "PID", "HOST", "LOGIN", "IDLE", "TYPE", "SESSION", "ID", "EXIT", "IPV6")
		#print f % (x.ut_user, x.ut_line, x.ut_pid, x.ut_host, time.ctime(x.ut_tv[0]), z, x.ut_type, x.ut_session, x.ut_id, x.ut_exit, x.ut_addr_v6)

		a = []
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


	def __cidle(self):
		"""grab all the client idle data that has been dumped into the
		shared folder, and process it in a mostly safe way."""
		import os
		import config
		import yamlhelp
		d = {'idle': [], 'users': [], 'line': [], 'max': None, 'min': None, 'len': 0}

		clients = os.listdir(os.path.join(config.SHAREDDIR, config.CIDLEPATH))
		t = time.time()
		for i in clients:
			# get the data from that particular client
			g = yamlhelp.yamlhelp(os.path.join(config.SHAREDDIR, config.CIDLEPATH, i))
			data = g.get_yaml()

			# apparently some of these could be None (and cause the program to die)
			if (type(data) == type({})) and (type(data['cidle']) == type({})):

				# when a user logs out, or if a client eva program is killed,
				# the files are still hanging around reporting their original
				# (incorrect) idle time, so after some threshold ignore them.
				if (t - data['tsync']) < config.STALETIME:
					# occasionally (for some magical reason) we
					# get an empty list which we should ignore.
					aa = len(data['cidle']['idle'])
					bb = len(data['cidle']['users']
					cc = len(data['cidle']['line'])
					dd = data['cidle']['len']
					if (type(dd) == type(1)) and (dd > 0) and (aa == bb == cc == dd):
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
						for j in range(data['cidle']['len']):
							z = data['cidle']['idle'][j] + ( t - data['tsync'] )

							if d['max'] == None: d['max'] = z
							if d['min'] == None: d['min'] = z
							d['max'] = max(d['max'], z)	# set the new max
							d['min'] = min(d['min'], z)	# set the new min

							d['idle'].append(z)
							d['users'].append( data['cidle']['users'][j] )
							d['line'].append( data['cidle']['line'][j] )
							d['len'] = d['len'] + 1

		return d




def put_cidle():
	"""stores the result of an idle() call in the shared
	directory, to be later read by the cidle() function."""
	import getpass
	import yamlhelp

	g = yamlhelp.yamlhelp(os.path.join(config.SHAREDDIR, config.CIDLEPATH, getpass.getuser()))
	g.put_yaml({'tsync': time.time(), 'cidle': ???i.idle(tick=True)???   })


def clean_cidle():


