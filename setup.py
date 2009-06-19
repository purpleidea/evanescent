#!/usr/bin/python

import distutils.core	#from distutils.core import setup, Extension
import os
import shutil		# for copying a file
import atexit		# for deleting the copied file

NAME = 'evanescent'

# add the extension if we're going to need it
ext_modules = []
if os.name == 'posix':
	ext_modules.append(
		distutils.core.Extension('evanescent.idle._x11_idle', ['evanescent/idle/_x11_idle.c'], libraries = ['Xss'])
	)

data_files = []
# add the icon
data_files.append( ('share/%s' % NAME, ['files/evanescent.png']) )
data_files.append( ('share/%s' % NAME, ['files/evanescent.svg']) )
data_files.append( ('share/%s' % NAME, ['COPYING']) )
data_files.append( ('share/%s' % NAME, ['AUTHORS']) )
data_files.append( ('share/%s' % NAME, ['VERSION']) )

# add the .yaml config file
if os.name == 'posix': shutil.copyfile('files/evanescent.conf.yaml.example', 'files/evanescent.conf.yaml')
elif os.name == 'nt': shutil.copyfile('files/evanescent.conf.yaml.wexample', 'files/evanescent.conf.yaml')
def cprm():
	"""remove the earlier copied file."""
	os.remove('files/evanescent.conf.yaml')
atexit.register(cprm)
# TODO: it would make more sense if distutils could rename a file, this way we
# wouldn't have to change the name of the file around.
data_files.append( ('/etc/', ['files/evanescent.conf.yaml']) )
# see: http://standards.freedesktop.org/autostart-spec/autostart-spec-latest.html
# and: http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
data_files.append( ('/etc/xdg/autostart/', ['files/evanescent.desktop']) )
data_files.append( ('/etc/event.d/', ['files/evanescent.upstart']) )

def get_version():
	"""little function that pulls the version from a text file."""
	# TODO: put these utility functions into a separate module
	# NOTE: this is copied from the code in eva.py
	try:
		f = open('VERSION', 'r')
		return f.read().strip()
	except IOError:
		return '0.0'
	finally:
		f.close()
		f = None


# setup
distutils.core.setup(
	name=NAME,
	version=get_version(),
	packages=['evanescent', 'evanescent.idle', 'evanescent.logout'],
	package_dir={'evanescent':'evanescent'},
	ext_modules=ext_modules,
	# list of miscellaneous extra modules to include
	py_modules=['yamlhelp'],
	data_files=data_files,
	# daemon and client scripts respectively
	scripts=['eva.py', 'evanescent_daemon.py']
)

