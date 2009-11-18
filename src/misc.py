#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Misc helper functions for evanescent machine idle detection and shutdown tool.

This is an assortment of small functions that don't belong anywhere important.
"""
# Copyright (C) 2008-2009  James Shubin, McGill University
# Written for McGill University by James Shubin <purpleidea@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import getpass

__all__ = ['console_msg', 'do_nologin', 'uptime', 'get_authors', 'get_license', 'get_version', 'get_home']

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
	"""stops new logins from happening, displays message if they try."""

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


def get_authors(wd=None, split=None):
	"""little function that pulls the authors from a text file. if split is
	True, then it returns the valid authors before the first line break and
	if split is False, then it returns the valid authors after the break."""
	if wd is None: wd = os.getcwd()
	try:
		f = open(os.path.join(wd, 'AUTHORS'), 'r')
		authors = f.readlines()
	except IOError:
		return []
	finally:
		try: f.close()
		except: pass
		f = None

	try:
		# find middle break
		middle = authors.index(os.linesep) - 1
	except ValueError:
		middle = None

	# clean up the authors (assume it's an author if there is an email)
	authors = [x.strip() for x in authors if '@' in x]

	if middle is None or split is None: return authors
	elif split: return authors[0:middle]
	else: return authors[middle:]


def get_license(wd=None):
	"""little function that pulls the license from a text file."""
	if wd is None: wd = os.getcwd()
	try:
		f = open(os.path.join(wd, 'COPYING'), 'r')
		return f.read().strip()
	except IOError:
		return None
	finally:
		try: f.close()
		except: pass
		f = None


def get_version(wd=None):
	"""little function that pulls the version from a text file."""
	if wd is None: wd = os.getcwd()
	try:
		f = open(os.path.join(wd, 'VERSION'), 'r')
		return f.read().strip()
	except IOError:
		return '0.0'
	finally:
		try: f.close()
		except: pass
		f = None


def get_home():
	"""returns the location of the users home directory."""
	return os.getenv('USERPROFILE', False) or os.getenv('HOME')


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

		elif sys.argv[1] in ['get_authors', 'get_license', 'get_version', 'get_home']:
			print eval(sys.argv[1])()
			sys.exit()

	print 'usage: %s uptime | do_nologin [message] | console_msg <message> | get_authors | get_license | get_version | get_home' % sys.argv[0]

