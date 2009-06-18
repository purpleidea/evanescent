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
import getpass

__all__ = ['console_msg', 'do_nologin', 'uptime']

def console_msg(message, line=None):
	"""send a simple console message out."""

	# TODO: sanitize message string for injection attacks and weird characters?
	message = str(message)
	who = getpass.getuser()

	if os.name == 'posix':
		if line is not None:
			os.system("echo '%s' | write %s %s &>/dev/null" % (message, who, line))
		else:
			os.system("echo '%s' | write %s &>/dev/null" % (message, who))

	elif os.name == 'nt':
		os.popen('net send %s %s' % (who, message))


def do_nologin(message=None):
	"""stops new logins from happening,
	displays message if they try."""

	if os.name == 'posix':
		# TODO: you need permission to change/create /etc/nologin,
		# so this script should check if it has permission first,
		# and then return true or false based on whether it succeeds
		# or not.
		if message:
			os.system("echo '%s' > /etc/nologin" % message)
		else:
			os.system("touch /etc/nologin")

	# TODO: fix this to return True/False based on if it worked or not.
	return True


def uptime():
	"""returns the uptime of the system in seconds"""
	# TODO: add dependency checking for the win32api module

	if os.name == 'nt':
		import win32api
		return int(win32api.GetTickCount()/1000)

	f = None
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


if __name__ == '__main__':
	import sys
	l = len(sys.argv)
	if l > 1 and sys.argv[1] in __all__:

		if sys.argv[1] == 'uptime' and l == 2:
			print uptime()
			sys.exit()

		elif sys.argv[1] == 'do_nologin' and l in [2, 3]:
			if l == 2: do_nologin()
			else: do_nologin(sys.argv[2])
			sys.exit()

		elif sys.argv[1] == 'console_msg' and l == 3:
			console_msg(sys.argv[2])
			sys.exit()

	print 'usage: %s uptime | do_nologin [message] | console_msg <message>' % sys.argv[0]

