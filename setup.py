#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Setup file for evanescent.

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

import distutils.core		#from distutils.core import setup, Extension
import os
import src.misc as misc		# for get_version
from jhelp import uninstall
				# custom distutils command for building manpages
from jhelp import build_manpages

# VARIABLES ###################################################################
NAME = 'evanescent'
ext_modules = []
data_files = []

# EXTENSIONS ##################################################################
if os.name == 'posix':
	ext_modules.append(
		distutils.core.Extension('evanescent.idle._x11_idle', ['src/idle/_x11_idle.c'], libraries=['Xss'])
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
	name=NAME,
	version=misc.get_version(),
	packages=['evanescent', 'evanescent.idle', 'evanescent.logout'],
	package_dir={'evanescent': 'src'},
	ext_modules=ext_modules,
	data_files=data_files,
	scripts=['evanescent-client', 'evanescent-daemon', 'evanescent-remote'],
	# add build_manpages command
	cmdclass={
		'install': uninstall.install, 'uninstall': uninstall.uninstall,
		'build_manpages': build_manpages.build_manpages,
	}
)

