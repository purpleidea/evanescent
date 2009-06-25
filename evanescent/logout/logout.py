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

__all__ = ['logout', 'shutdown', 'session']

if os.name == 'nt':
	from _wts import logmeoff as logout
	from _wts import shutdown as shutdown

elif os.name == 'posix':

	def logout():
		"""logout the current user's X session."""
		# TODO: there is probably a better / cleaner way to do this.
		# NOTE: On GNOME, this is best done by sending a log-out message
		# to GDM via the /var/run/gdm_socket Unix domain socket. On X11
		# without GNOME, this can be done by asking the background
		# process to send SIGINT to the user's x-session-manager.

		s = session()
		# FIXME: write this code... make it work... test it.
		if s == 'gnome': os.system('gnome-session-save --logout-dialog')
		else: os.system('killall --signal SIGINT x-session-manager')
		#os.system('killall --signal SIGINT gnome-session')


	def shutdown():
		"""shutdown the system now."""
		os.system('shutdown -P now shutdown by evanescent')

else: raise ImportError("operating system not supported")


def session():
	"""returns the name of the currently running window manager/desktop."""
	# this was adapter from:
	# http://gitweb.compiz-fusion.org/?p=fusion/misc/compiz-manager;a=blob;f=compiz-manager
	# FIXME: write this code... make it work... test it.
	# TODO: is there a better way to implement this ?
	if os.name == 'nt': return 'windows'
	elif os.getenv('KDE_FULL_SESSION') == 'true': return 'kde'
	elif os.getenv('GNOME_DESKTOP_SESSION_ID') != '': return 'gnome'
	#elif #BASH: if xprop -root _DT_SAVE_MODE | grep ' = \"xfce4\"$' >/dev/null 2>&1; then XFCE
	else: return ''


if __name__ == '__main__':
	import sys
	if len(sys.argv) == 2 and sys.argv[1] in __all__:

		if sys.argv[1] == 'shutdown': shutdown()
		elif sys.argv[1] == 'logout': logout()
		elif sys.argv[1] == 'session': session()

	else: print 'usage: %s logout | shutdown | session' % sys.argv[0]

