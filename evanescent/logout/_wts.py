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
"""Simple Python interface to the Windows Terminal Service API."""

# Based 99% on code and help from Alexandre Vassalotti <alexandre@peadrop.com>

import os
if os.name != 'nt':
	raise ImportError('This modules requires Windows 2000 or newer.')
import win32ts
import socket
import operator

__all__ = ['listusers', 'logoff', 'logmeoff', 'shutdown']

def _add_enum_constants(enum_constants):
	global state2name
	state2name = {}
	module_dict = globals()
	for i, name in enumerate(enum_constants):
		module_dict[name] = i
		state2name[i] = name

_enum_constants = (
	'WTSActive',
	'WTSConnected',
	'WTSConnectQuery',
	'WTSShadow',
	'WTSDisconnected',
	'WTSIdle',
	'WTSListen',
	'WTSReset',
	'WTSDown',
	'WTSInit'
)

_add_enum_constants(_enum_constants)
del _add_enum_constants
del _enum_constants

class WTSServer:
	def __init__(self, hostname):
		self.hostname = hostname
		self.handle = win32ts.WTSOpenServer(hostname)

	def close(self):
		win32ts.WTSCloseServer(self.handle)

	def __del__(self):
		self.close()


class SessionInfo(tuple):
	"""SessionInfo(session_id, state, username)"""
	__slots__ = ()

	def __new__(cls, session_id, state, username):
		return tuple.__new__(cls, (session_id, state, username))

	def __repr__(self):
		return 'SessionInfo(session_id=%s, state=%s, username=%s)' % self

	session_id = property(operator.itemgetter(0))
	state = property(operator.itemgetter(1))
	username = property(operator.itemgetter(2))


def listusers():
	"""list the users on the machine."""
	server = WTSServer(socket.gethostname())
	results = []
	for session in win32ts.WTSEnumerateSessions(server.handle):
		session_id = session['SessionId']
		state = session['State']
		username = win32ts.WTSQuerySessionInformation(
			server.handle, session_id, win32ts.WTSUserName)
		results.append(SessionInfo(session_id, state, username))
	return results

def logoff(session_id):
	"""log off a particular session."""
	if session_id < 0:
		raise ValueError('session ID must be non-negative')
	server = WTSServer(socket.gethostname())
	win32ts.WTSLogoffSession(server.handle, session_id, True)


def logmeoff():
	"""logs off the current user."""
	server = WTSServer(socket.gethostname())
	session_id = win32ts.ProcessIdToSessionId(os.getpid())
	return logoff(session_id)


def shutdown():
	"""shuts down the machine."""
	server = WTSServer(socket.gethostname())
	win32ts.ShutdownSystem(server.handle, win32ts.WTS_WSD_POWEROFF)

