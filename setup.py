#!/usr/bin/python
# TODO: this file needs some love
import distutils.core		#from distutils.core import setup, Extension
import os
import src.misc as misc		# for get_version
import uninstall
import build_manpages		# custom distutils command for building manpages

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
	data_files.append(('share/dbus-1/services/', ['files/ca.mcgill.cs.dazzle.evanescent.client.service']))
	data_files.append(('share/doc/%s/' % NAME, ['files/evanescent.conf.yaml.example']))
	data_files.append(('share/man/man1/', ['man/evanescent.1.gz']))
	data_files.append(('share/man/man1/', ['files/evanescent-daemon.1.gz']))
	data_files.append(('share/man/man1/', ['files/evanescent-client.1.gz']))
	data_files.append(('share/man/man1/', ['files/evanescent-remote.1.gz']))
	data_files.append(('share/man/man1/', ['files/evanescent-config.1.gz']))

# SETUP #######################################################################
distutils.core.setup(
	name = NAME,
	version = misc.get_version(),
	packages = ['evanescent', 'evanescent.idle', 'evanescent.logout'],
	package_dir = {'evanescent':'src'},
	ext_modules = ext_modules,
	# list of miscellaneous extra modules to include
	py_modules = ['yamlhelp', 'logginghelp', 'manhelp'],
	data_files = data_files,
	scripts = ['evanescent-client', 'evanescent-daemon', 'evanescent-remote'],
	# add build_manpages command
	cmdclass = {
		'uninstall': uninstall.uninstall,
		'build_manpages': build_manpages.build_manpages
	}
)

