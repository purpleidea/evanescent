#!/usr/bin/python
# TODO: this file needs some love
import distutils.core		#from distutils.core import setup, Extension
import os
import evanescent.misc as misc	# for get_version
import shutil			# for copying a file
import atexit			# for deleting the copied file


# VARIABLES ###################################################################
NAME = 'evanescent'
ext_modules = []
data_files = []


# EXTENSIONS ##################################################################
if os.name == 'posix':
	ext_modules.append(
		distutils.core.Extension('evanescent.idle._x11_idle', ['evanescent/idle/_x11_idle.c'], libraries = ['Xss'])
	)


# DATA FILES ##################################################################
data_files.append(('share/%s' % NAME, ['files/evanescent.png']))
data_files.append(('share/%s' % NAME, ['files/evanescent.svg']))
data_files.append(('share/%s' % NAME, ['COPYING']))
data_files.append(('share/%s' % NAME, ['AUTHORS']))
data_files.append(('share/%s' % NAME, ['VERSION']))
# see: http://standards.freedesktop.org/autostart-spec/autostart-spec-latest.html
# and: http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
if os.name == 'posix':
	data_files.append(('/etc/xdg/autostart/', ['files/evanescent.desktop']))
	data_files.append(('/etc/event.d/', ['files/evanescent.upstart']))





# add the .yaml config file
#if os.name == 'posix': shutil.copyfile('files/evanescent.conf.yaml.example', 'files/evanescent.conf.yaml')
#elif os.name == 'nt': shutil.copyfile('files/evanescent.conf.yaml.wexample', 'files/evanescent.conf.yaml')
#def cprm():
#	"""remove the earlier copied file."""
#	os.remove('files/evanescent.conf.yaml')
#atexit.register(cprm)

# TODO: it would make more sense if distutils could rename a file, this way we
# wouldn't have to change the name of the file around.
#data_files.append( ('/etc/', ['files/evanescent.conf.yaml']) )

if os.name == 'posix': data_files.append( ('/etc/', ['files/evanescent.conf.yaml.example']) )
elif os.name == 'nt': data_files.append( ('/etc/', ['files/evanescent.conf.yaml.wexample']) )#does this need changing from /etc to ?






# SETUP #######################################################################
distutils.core.setup(
	name=NAME,
	version=misc.get_version(),
	packages=['evanescent', 'evanescent.idle', 'evanescent.logout'],
	package_dir={'evanescent':'evanescent'},
	ext_modules=ext_modules,
	# list of miscellaneous extra modules to include
	py_modules=['yamlhelp', 'logginghelp'],
	# the data files
	data_files=data_files,
	# client and daemon scripts respectively
	scripts=['eva.py', 'evanescent_daemon.py']
)

