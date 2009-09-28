#!/usr/bin/python
# TODO: this file needs some love
import distutils.core		#from distutils.core import setup, Extension
import os
import src.misc as misc		# for get_version

# VARIABLES ###################################################################
NAME = 'evanescent'
ext_modules = []
data_files = []

# EXTENSIONS ##################################################################
if os.name == 'posix':
	ext_modules.append(
		distutils.core.Extension('evanescent.idle._x11_idle', ['src/idle/_x11_idle.c'], libraries = ['Xss'])
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
	data_files.append(('/usr/share/dbus-1/services/', ['files/ca.mcgill.cs.dazzle.evanescent.client.service']))

if os.name == 'posix':
	#data_files.append( ('/etc/', ['files/evanescent.conf.yaml']) )
	data_files.append( ('/etc/', ['files/evanescent.conf.yaml.example']) )


# SETUP #######################################################################
distutils.core.setup(
	name=NAME,
	version=misc.get_version(),
	packages=['evanescent', 'evanescent.idle', 'evanescent.logout'],
	package_dir={'evanescent':'src'},
	ext_modules=ext_modules,
	# list of miscellaneous extra modules to include
	py_modules=['yamlhelp', 'logginghelp'],
	data_files=data_files,
	scripts=['evanescent-client', 'evanescent-daemon', 'evanescent-remote']
)

