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

def do_nologin(message=None):
	"""stops new logins from happening,
	displays message if they try."""
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
	"""broadcasts a write to all the cli/gtk clients to say goodbye"""
	#FIXME: in the future we can have this be a more powerful library...
	# it could use libnotify... and do fancy talking to gtk
	# it could use write
	# it could specify just a user or multiple users...
	# it could specify particular lines (eg: terminals, like: tty7, or pts/0)
	# it could do a combination of the above
	# but for now it doesn't do anything.

	# TODO: sanitize message string for injection attacks and weird characters?
	message = str(message)
	if not(who.has_key('users')): return False
	if who.has_key('line') and len(who['users']) != len(who['line']): raise AssertionError
	if type(who['users']) == type([]):
		for i in range(len(who['users'])):
			if who.has_key('line'):
				os.system("echo '%s' | write %s %s &>/dev/null" % (message, who['users'][i], who['line'][i]))
			else:
				os.system("echo '%s' | write %s &>/dev/null" % (message, who['users'][i]))

	return True


def do_shutdown():
	"""shuts down the system"""
	os.system("shutdown -P now bye!")

