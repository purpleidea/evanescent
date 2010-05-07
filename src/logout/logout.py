#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Logout functions.

Logout functions to be called from within a users session on any platform.
"""
# Copyright (C) 2008-2010  James Shubin, McGill University
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

_ = lambda x: x			# add fake gettext function until i fix up i18n

__all__ = ['logmeout', 'shutdown', 'session']

def session():
	"""returns the name of the currently running window manager/desktop."""
	# this was adapted from:
	# http://gitweb.compiz-fusion.org/?p=fusion/misc/compiz-manager;a=blob;f=compiz-manager
	# FIXME: write this code... make it work... test it.
	# TODO: is there a better way to implement this ?
	if os.name == 'nt': return 'windows'
	elif os.getenv('KDE_FULL_SESSION') == 'true': return 'kde'
	elif os.getenv('GNOME_DESKTOP_SESSION_ID') != '': return 'gnome'
	#elif #BASH: if xprop -root _DT_SAVE_MODE | grep ' = \"xfce4\"$' >/dev/null 2>&1; then XFCE
	else: return ''


if os.name == 'nt':
	from _wts import logmeoff as logmeout
	from _wts import shutdown as shutdown

elif os.name == 'posix':

	s = session()
	# TODO: can we fix the difference between _gnome and _kde4 logmeout
	# functions so that they either both block until action or not ?
	if s == 'gnome':
		import _gnome
		LOGOUT_CONFIRM = _gnome.LOGOUT_MODE_NORMAL
		LOGOUT_FORCE = _gnome.LOGOUT_MODE_FORCE
		logmeout = _gnome.logmeout

	elif s == 'kde':
		import _kde4
		LOGOUT_CONFIRM = _kde4.SHUTDOWN_CONFIRM_YES
		LOGOUT_FORCE = _kde4.SHUTDOWN_CONFIRM_NO
		logmeout = _kde4.logmeout

	else:
		LOGOUT_CONFIRM = None
		LOGOUT_FORCE = None
		def logout(mode=LOGOUT_CONFIRM):
			"""logout the current user's X session."""
			# TODO: there is probably a better / cleaner way to do this.
			# NOTE: On GNOME, this is best done by sending a log-out message
			# to GDM via the /var/run/gdm_socket Unix domain socket. On X11
			# without GNOME, this can be done by asking the background
			# process to send SIGINT to the user's x-session-manager.

			# TODO: rewrite this code... make it work nicely
			os.system('killall --user %s --exact x-session-manager' % os.getlogin())


	def shutdown():
		"""shutdown the system now."""
		# TODO: could be replaced by dbus calls to the session manager
		os.system('shutdown -P now shutdown by evanescent')

else: raise ImportError('operating system not supported')


if __name__ == '__main__':
	import sys
	if len(sys.argv) == 2 and sys.argv[1] in __all__:

		if sys.argv[1] == 'shutdown': shutdown()
		elif sys.argv[1] == 'logmeout': logmeout()
		elif sys.argv[1] == 'session': session()

	else: print 'usage: %s logmeout | shutdown | session' % sys.argv[0]

