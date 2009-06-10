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

import os
import time
import config
import yamlhelp

def do_nologin(message=None):
	"""stops new logins from happening,
	displays message if they try."""

	if os.name == 'posix':
		# FIXME: you need permission to change/create /etc/nologin,
		# so this script should check if it has permission first,
		# and then return true or false based on whether it succeeds
		# or not.
		if message:
			os.system("echo '%s' > /etc/nologin" % message)
		else:
			os.system("touch /etc/nologin")

	# FIXME: fix this to return True/False based on if it worked or not.
	return True


def do_broadcast(message, who={'users': []}):
	"""broadcasts a message to all the cli/gtk clients."""
	#FIXME: in the future we can have this be a more powerful library...
	# it could use libnotify... and do fancy talking to gtk
	# it could use write
	# it could specify just a user or multiple users...
	# it could specify particular lines (eg: terminals, like: tty7, or pts/0)
	# it could do a combination of the above

	if not(who.has_key('users')): return False
	if who.has_key('line') and len(who['users']) != len(who['line']): raise AssertionError
	# TODO: sanitize message string for injection attacks and weird characters?
	message = str(message)
	if type(who['users']) == type([]):
		for i in range(len(who['users'])):

			# send a message to all clients through text file
			# ipc. using a text file to pass messages is both
			# simple and compatible in both windows and unix.

			f = yamlhelp.yamlhelp(os.path.join(config.SHAREDDIR, config.MSGSUBDIR, who['users'][i]))
			try:
				# make a new message id... have it be slightly larger than the last.
				result = f.get_yaml()
				if not(type(result) == type([])) or (len(result) < 1): raise IOError
				new_id = max([ x['id'] for x in result ]) + 1

			except IOError:
				new_id = 1

			yaml_msg = [ {'id': new_id, 'tsync': time.time(), 'msg': message} ]
			# append a message to the text file message queue
			f.put_yaml(yaml_msg, mode='a')

			if os.name == 'posix':
				if who.has_key('line'):
					os.system("echo '%s' | write %s %s &>/dev/null" % (message, who['users'][i], who['line'][i]))
				else:
					os.system("echo '%s' | write %s &>/dev/null" % (message, who['users'][i]))

			elif os.name == 'nt':
				os.popen('net send %s %s' % (who['users'][i], message))

	return True


def do_shutdown():
	"""takes down the system in some manner."""
	# here are a list of allowed take-down commands to run.
	# TODO: add more valid take-down commands to this list
	if os.name == 'posix':
		allowed = ['shutdown -P now bye!', 'pm-suspend', 'pm-hibernate', 'pm-suspend-hybrid']
	elif os.name == 'nt':
		allowed = ['shutdown.exe -s -t 00 -c "bye!"']

	if config.TDCOMMAND in allowed: os.system(config.TDCOMMAND)


def uptime():
	"""returns the uptime of the system in seconds"""
	# TODO: add dependency checking for the win32api module

	if os.name == 'nt':
		import win32api
		return int(win32api.GetTickCount()/1000)

	sec = -1
	try:
		f = open('/proc/uptime')
		contents = f.read().split()
		sec = int(float(contents[0]))

	except e:
		pass

	finally:
		if f != None: f.close()
		f = None

	return sec


