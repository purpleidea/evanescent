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

def logmeout():
	"""sends a logout command through dbus to the session. this function
	works for gnome 2.0, and returns immediately. (it does not block)"""
	# OLD but equivalent: os.system('gnome-session-save --logout-dialog')

	# TODO: can the uint32 0 be changed to do something better or different?
	"""trace from dbus-monitor:
	method call sender=:1.543 -> dest=org.gnome.SessionManager path=/org/gnome/SessionManager; interface=org.gnome.SessionManager; member=Logout
	uint32 0
	"""
	bus = dbus.SessionBus()
	try:
		remote_object = bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')

		# specify the dbus_interface in each call
		remote_object.Logout(0, dbus_interface='org.gnome.SessionManager')

		# or create an Interface wrapper for the remote object
		#iface = dbus.Interface(remote_object, 'org.gnome.SessionManager')
		#iface.Logout(0)

		# introspection is automatically supported
		#print remote_object.Introspect(dbus_interface='org.freedesktop.DBus.Introspectable')

	except dbus.DBusException, e:
		return False

	return True


if __name__ == '__main__':
	logmeout()

