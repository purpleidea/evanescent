#!/usr/bin/python

import sys
import getopt
import dbus
from evanescent.edbus import _service, _interface, _path	# pull strings

def usage():
	"""prints out the usage."""

	string = './%s: ?' % sys.argv[0]
	print string


def main(argv):
	"""main function."""

	# setup getopt
	try:
		# TODO: replace with optparse module
		opts, args = getopt.getopt(argv, 'hdqg:', ['help', 'quit', 'hello='])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	# make dbus
	try:
		bus = dbus.SessionBus()
		remote_object = bus.get_object(_service, _path)
		iface = dbus.Interface(remote_object, _interface)

	except dbus.DBusException, e:
		# this error occurs when the evanescent-client program isn't
		# running because dbus will attempt to start a program that
		# serves a request if it is not present. to do this, it will
		# search for a special file in the /usr/share/dbus-1/ folder
		# which if non existent will throw the below error. checking
		# _dbus_error_name is the only way i know to detect for it.
		if e._dbus_error_name == 'org.freedesktop.DBus.Error.ServiceUnknown':
			print 'please verify that the evanescent client is running.'
		else: usage()
		sys.exit(1)

	# go through args
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			usage()

		elif opt == '-d':
			#debug
			pass

		if opt == '--hello':
			if len(arg) < 1:
				usage()
			else: iface.Hello(arg)

		elif opt in ('-q', '--quit'):
			iface.Quit()

		else: 
			assert False, 'unhandled option'

		sys.exit()

if __name__ == '__main__':
	main(sys.argv[1:])

