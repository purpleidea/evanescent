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
	works for kde 4.0, and returns after the dialog ends. (it blocks)"""

	# TODO: can the int32 's be changed to do something better or different?
	"""dbus-monitor:
	method call sender=:1.12 -> dest=org.kde.ksmserver path=/KSMServer; interface=org.kde.KSMServerInterface; member=logout
	int32 -1
	int32 0
	int32 -1
	"""

	bus = dbus.SessionBus()
	try:
		remote_object = bus.get_object('org.kde.ksmserver', '/KSMServer')

		# specify the dbus_interface in each call
		remote_object.logout(-1, 0, -1, dbus_interface='org.kde.KSMServerInterface')

		# or create an Interface wrapper for the remote object
		#iface = dbus.Interface(remote_object, 'org.kde.KSMServerInterface')
		#iface.logout(-1, 0, -1)

		# introspection is automatically supported
		#print remote_object.Introspect(dbus_interface='org.freedesktop.DBus.Introspectable')

	except dbus.DBusException, e:
		return False

	return True


if __name__ == '__main__':
	logmeout()

