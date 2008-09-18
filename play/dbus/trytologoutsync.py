#!/usr/bin/python

import dbus

def gnome_logout():
	"""sends a logout command through dbus to the session."""

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


def kde4_logout():
	"""sends a logout command through dbus to the session."""

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
	#logout()

