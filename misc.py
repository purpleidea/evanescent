#!/usr/bin/python

import os

def do_nologin(message=None):
	"""stops new logins from happening,
	displays message if they try."""
	# FIXME: you need permission to change/create /etc/nologin,
	# so this script should check if it has permission first,
	# and then return true or false based on whether it succeeds
	# or not.
	if message:
		os.system("echo '%s' > /etc/nologin" % message)
	else:
		os.system("touch /etc/nologin")

	# FIXME: fix this to return True/False based on if it worked or not.
	return True



def do_broadcast(message=None):
	"""broadcasts a write to all the cli/gtk clients to say goodbye"""
	#FIXME: in the future we can have this be a more powerful library...
	# it could use libnotify... and do fancy talking to gtk
	# it could use write
	# it could specify just a user or multiple users...
	# it could specify particular lines (eg: terminals, like: tty7, or pts/0)
	# it could do a combination of the above
	# but for now it doesn't do anything.
	pass


def do_shutdown():
	"""shuts down the system"""
	os.system("shutdown -P now bye!")
