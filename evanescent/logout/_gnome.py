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
import dbus

__all__ = ['logmeout']

LOGOUT_MODE_NORMAL = 0
LOGOUT_MODE_NO_CONFIRMATION = 1
LOGOUT_MODE_FORCE = 2

def logmeout(mode=LOGOUT_MODE_NORMAL):
	"""sends a logout command through dbus to the session. this function
	works for gnome 2.0, and returns immediately. (it does not block)"""
	# OLD: (but equivalent) os.system('gnome-session-save --logout-dialog')
	# DOCS: http://www.gnome.org/~mccann/gnome-session/docs/gnome-session.html#org.gnome.SessionManager.Logout
	# SOURCE: http://git.gnome.org/cgit/gnome-session/tree/gnome-session/gsm-manager.h

	bus = dbus.SessionBus()
	try:
		remote_object = bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')

		# specify the dbus_interface in each call
		remote_object.Logout(mode, dbus_interface='org.gnome.SessionManager')

	except dbus.DBusException, e:
		return False

	return True


if __name__ == '__main__':
	logmeout()

