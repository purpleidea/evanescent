#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Evanescent machine idle detection and shutdown tool remote.

This is a utility that allows a user to easily control their client evanescent.
Read the man pages for more info.
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

import os
import sys
import optparse
import dbus
from config import _service, _interface, _path			# pull strings
import config							# config module
import misc						# misc functions module

class evanescent_remote:

	def print_error(self, message):
		"""print an error message. match the look of optparse messages."""
		print '%s: error: %s' % (os.path.basename(sys.argv[0]), message)
		sys.exit(1)


	def main(self):
		"""main function."""

		# command line argument parsing
		description = 'a command line front end to accessing the evanescent '\
		'client through the dbus session bus interface for evanescent. the '\
		'options are intended to be useful to the evanescent power user or to '\
		'debug, test and demo the features of evanescent easily and directly.'
		version = misc.get_version(config.SHAREDDIR)
		parser = optparse.OptionParser(description=description, version=version)
		parser.add_option('', '--authors', dest='authors', action='store_true', help='show the authors')
		parser.add_option('', '--license', dest='license', action='store_true', help='show the license')
		parser.add_option('', '--hello', dest='hello', type='string', metavar='<MSG>', help='send message to client')
		parser.add_option('-q', '--quit', dest='quit', action='store_true', help='send quit to the client')
		parser.add_option('-p', '--poke', dest='poke', action='store_true', default=True, help='poke the client [on by default]')
		parser.add_option('-P', '--dont-poke', dest='poke', action='store_false', help='don\'t poke the client')
		parser.add_option('-s', '--show', dest='show', type='int', metavar='<N>', help='cause the notification icon to appear for <N> seconds')
		choices = {'true': True, 'false': False, 'reset': None}	# tristate
		parser.add_option('', '--force-idle', dest='idle', choices=choices.keys(), metavar='<state>', help='force simulated idle state')
		parser.add_option('', '--force-excl', dest='excl', choices=choices.keys(), metavar='<state>', help='force simulated excluded state')

		(options, args) = parser.parse_args()

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
				# NOTE: a service file is part of this code, it should
				# be at: <above_path>/services/<edbus._service>.service
				t = '%s%s' % (_service, '.service')	# the filename
				t = os.path.join('/usr/share/dbus-1/', 'services/', t)
				if os.path.isfile(t):
					print_error('please verify that the client is running.')
				else:
					print_error('service file not found at: %s' % t)

			elif e._dbus_error_name == 'org.freedesktop.DBus.Error.Spawn.ChildExited':
				print_error('client startup mode is probably false.')
			else: print_error(e)

		# run any actions
		if options.show:
			iface.ShowMenu(options.show)

		if options.idle:
			if choices[options.idle] is None:
				iface.ResetForceIdleFlag()
			else: iface.SetForceIdleFlag(choices[options.idle])

		if options.excl:
			if choices[options.excl] is None:
				iface.ResetForceExcludedFlag()
			else: iface.SetForceExcludedFlag(choices[options.excl])

		if options.poke:
			iface.poke()

		if options.hello:
			iface.Hello(options.hello)

		if options.quit:
			iface.Quit()
			sys.exit()

		if options.authors:
			for x in misc.get_authors():
				print x

		if options.license:
			# TODO: format this with a pager
			print misc.get_license()

if __name__ == '__main__':
	obj = evanescent_remote()
	obj.main()

