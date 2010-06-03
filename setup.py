#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup file for evanescent.

Supported commands include a customized `install' target, and a magic
`uninstall' target.
"""
# Copyright (C) 2008-2010  James Shubin, McGill University
# Written for McGill University by James Shubin <purpleidea@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys			# for sys.modules
import pydoc
import distutils.core		#from distutils.core import setup, Extension
from jhelp import misc		# for get_version, get_capitalized_files
from jhelp import uninstall	# custom distutils uninstall & install commands
				# custom distutils command for building manpages
from jhelp import build_manpages
#from jhelp import dependencies	# TODO
from src import prefix		# used to find the name of this project

# VARIABLES ###################################################################
NAME = prefix.name('src')		# should be the name of this dir
# this pulls the one-line description and long description from the docstring
DESCRIPTION, LDESCRIPTION = pydoc.splitdoc(pydoc.getdoc(sys.modules[__name__]))

# see: http://standards.freedesktop.org/autostart-spec/autostart-spec-latest.html
# and: http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html

# DEPENDENCIES ################################################################
#dependencies.check()		# TODO

# SETUP #######################################################################
distutils.core.setup(
	name=NAME,
	version=misc.get_version(),
	author='James Shubin',
	author_email='purpleidea@gmail.com',
	url='http://www.cs.mcgill.ca/~james/code/',
	description=DESCRIPTION,
	long_description=LDESCRIPTION,
	# http://pypi.python.org/pypi?%3Aaction=list_classifiers
	classifiers=[
		'Environment :: X11 Applications :: GTK',
		'Environment :: X11 Applications :: GTK',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU Affero General Public License v3',
		'Topic :: System :: Systems Administration',
	],
	packages=['evanescent', 'evanescent.idle', 'evanescent.logout'],
	package_dir={NAME: 'src'},
	ext_modules=[
		distutils.core.Extension('evanescent.idle._x11_idle', ['src/idle/_x11_idle.c'], libraries=['Xss']),
		],
	data_files=[
		('share/%s' % NAME, ['Makefile']),
		('share/%s' % NAME, misc.get_capitalized_files()),
		('/etc/xdg/autostart/', ['files/evanescent.desktop']),
		('/etc/event.d/', ['files/evanescent.upstart']),
		# XXX: i bet that dbus doesn't look in /usr/local/share/dbus-1/
		('/usr/share/dbus-1/services/', ['files/ca.mcgill.cs.dazzle.evanescent.client.service']),
		('share/doc/%s/' % NAME, ['files/evanescent.conf.yaml.example']),
		# images
		('share/%s' % NAME, ['files/evanescent.png']),
		('share/%s' % NAME, ['files/evanescent.svg']),
		# man page related
		('share/%s' % NAME, ['files/evanescent.1.template']),
		('share/man/man1/', ['man/evanescent.1.gz']),
		# FIXME: these should all be copies of the main file
		#('share/man/man1/', ['files/evanescent-daemon.1.gz']),
		#('share/man/man1/', ['files/evanescent-client.1.gz']),
		#('share/man/man1/', ['files/evanescent-remote.1.gz']),
		#('share/man/man1/', ['files/evanescent-config.1.gz']),
	],
	scripts=['evanescent-client', 'evanescent-daemon', 'evanescent-remote'],
	cmdclass={
		'install': uninstall.install, 'uninstall': uninstall.uninstall,
		'build_manpages': build_manpages.build_manpages,
	}
)

