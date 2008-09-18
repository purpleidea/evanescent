#!/usr/bin/python



# TODO:  figure out how to run the xssidle code on various different xsessions... 
# it seems it only works on os.environ['DISPLAY'] hmmm... basically i want to end
# up with the idle time for any logged in user. whether it be through X or ssh -X



import dbus
import os

#print os.environ['DISPLAY']


def uids():
	#FIXME: this is a hack, do this with utmp
	"""return a list of logged in uid's."""

	#return [os.getuid()]
	#return [118]
	return [1001]
	#return [17949, 118]



def xssidle(display=None):
	"""return idle time in ms from X11 xss extensions."""
	# FIXME: this may or may not suffer from the dpms bug.
	import os
	import ctypes
	import getpass
	if display is None: display = os.environ['DISPLAY']

	class XScreenSaverInfo(ctypes.Structure):
		"""typedef struct { ... } XScreenSaverInfo;"""
		_fields_ = [
			('window',      ctypes.c_ulong),	# screen saver window
			('state',       ctypes.c_int),		# off,on,disabled
			('kind',        ctypes.c_int),		# blanked,internal,external
			('since',       ctypes.c_ulong),	# milliseconds
			('idle',        ctypes.c_ulong),	# milliseconds
			('event_mask',  ctypes.c_ulong)		# events
		]

	xlib = ctypes.cdll.LoadLibrary('libX11.so')
	# TODO: can this be modified to query a different Xdisplay?
	# this way it can be run as root in the daemon, and doesn't
	# have to depend on the client running an eva style program

	dpy = xlib.XOpenDisplay(display)
	print 'dpy: %s' % dpy
	#if dpy == 0: return -1 # ???

	root = xlib.XDefaultRootWindow(dpy)
	print 'No segmentation fault'
	xss = ctypes.cdll.LoadLibrary('libXss.so')
	xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
	xss_info = xss.XScreenSaverAllocInfo()
	xss.XScreenSaverQueryInfo(dpy, root, xss_info)

	result = int(xss_info.contents.idle)			# idle time in milliseconds

	return result

	# FIXME: find out how to get the line associated with the current X server running on $DISPLAY
	#return {'idle': [result], 'users': [getpass.getuser()], 'line': ['?'], 'max': result, 'min': result, 'len': 1}







#print 'xssidle: %s' % xssidle(':0.0')
#print 'xssidle: %s' % xssidle('localhost:21.0')
print 'xssidle: %s' % xssidle('localhost:21')




import sys
sys.exit(0)


os.system('echo uid dpy idle > output')

# get the consolekit manager
bus = dbus.SystemBus()
manager_obj = bus.get_object('org.freedesktop.ConsoleKit', '/org/freedesktop/ConsoleKit/Manager')
manager = dbus.Interface(manager_obj, 'org.freedesktop.ConsoleKit.Manager')


for uid in uids():
	# for each of a uid's sessions..
	for ssid in manager.GetSessionsForUnixUser(uid):
		obj = bus.get_object('org.freedesktop.ConsoleKit', ssid)
		session = dbus.Interface(obj, 'org.freedesktop.ConsoleKit.Session')
		# Get the X11 display name
		dpy = session.GetX11Display()
		if dpy:

			idle = -1
			idle = xssidle(str(dpy) + '.0')

			os.system('echo %s %s %s >> output' % (uid, dpy, idle))
			break

