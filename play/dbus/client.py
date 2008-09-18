#!/usr/bin/env python

usage = """Usage:
python example-service.py &
python example-client.py
python example-client.py --exit-service
"""

import sys
from traceback import print_exc

import dbus

def main():
	bus = dbus.SessionBus()

	try:
		remote_object = bus.get_object("ca.mcgill.cs.dazzle.evanescent.eva", "/Eva")

		# you can either specify the dbus_interface in each call...
		hello_reply_list = remote_object.HelloWorld("Hello from client.py!",
		dbus_interface = "ca.mcgill.cs.dazzle.evanescent.eva.Interface")
	except dbus.DBusException:
		print_exc()
		print usage
		sys.exit(1)

	print (hello_reply_list)


	#print type(hello_reply_list) is list	# won't work
	print isinstance(hello_reply_list, list)	# works as it allows subclasses.

	# ... or create an Interface wrapper for the remote object
	iface = dbus.Interface(remote_object, "ca.mcgill.cs.dazzle.evanescent.eva.Interface")

	hello_reply_tuple = iface.GetTuple()

	print hello_reply_tuple

	hello_reply_dict = iface.GetDict()

	print hello_reply_dict

	iface.main_quit()
	sys.exit()

	# D-Bus exceptions are mapped to Python exceptions
	try:
		iface.RaiseException()
	except dbus.DBusException, e:
		#print str(e)
		print 'exception caught!'

	# introspection is automatically supported
	#print remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")

	if sys.argv[1:] == ['--exit-service']:
		iface.Exit()

if __name__ == '__main__':
	main()

