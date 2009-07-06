#!/usr/bin/python
"""
    Evanescent machine idle detection and shutdown tool.
    Copyright (C) 2008  James Shubin, McGill University
    Written for McGill University by James Shubin <purpleidea@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import dbus
import dbus.service

__all__ = ['_service', '_interface', '_path', 'Eva', 'DemoException']

_service = 'ca.mcgill.cs.dazzle.evanescent.eva'
_interface = _service + '.Interface'
_path = '/Eva'

class DemoException(dbus.DBusException):
	_dbus_error_name = _service + '.DemoException'


class Eva(dbus.service.Object):
	"""class for dbus eva session."""

	def __init__(self, s, bus_name, path=_path):
		"""initialize the class. the s parameter is where we get a
		reference to the `self' of the calling class so that this class
		can call the functions and access the properties of the caller
		and interact intelligently."""

		# store a reference to the main eva `self'
		self.self = s

		# the object path
		dbus.service.Object.__init__(self, bus_name, path)


	@dbus.service.method(_interface, in_signature='', out_signature='')
	def RaiseException(self):
		"""example dbus exception."""
		raise DemoException('This is an exception!')


	@dbus.service.method(_interface, in_signature='', out_signature='')
	def Poke(self):
		"""poke the client, causing it to wake from sleep."""
		self.self.log.debug('poke received through dbus')
		self.self.poke()


	@dbus.service.method(_interface, in_signature='i', out_signature='')
	def ShowMenu(self, seconds):
		"""cause the notification icon to display for <n> seconds. the
		icon will auto hide itself in <n> seconds if the <n> value is
		greater than 0."""
		self.self.log.debug('icon made visible through dbus')
		self.self.icon_visibility(True)	# show it now
		# then, potentially hide it in a bit
		print seconds
		print type(seconds)
		#seconds = int(seconds)
		if seconds > 0:
			self.self.log.debug('icon will hide in %d second(s).' % seconds)
			self.self.icon_visibility(seconds=seconds, visibility=False)


	@dbus.service.method(_interface, in_signature='s', out_signature='')
	def Hello(self, message):
		"""send a hello message to the user. mostly for example fun."""
		self.self.msg(message=str(message), title='incoming message')


	@dbus.service.method(_interface, in_signature='b', out_signature='')
	def SetForceIdleFlag(self, flag):
		"""sets the boolean force_idle flag."""
		flag = bool(flag)	# since it comes in differently
		self.self.log.debug('force_idle flag received through dbus')
		self.self.force_idle = flag


	@dbus.service.method(_interface, in_signature='', out_signature='')
	def ResetForceIdleFlag(self):
		"""reset the force_idle flag."""
		self.self.log.debug('resetting force_idle flag through dbus')
		self.self.force_idle = None


	@dbus.service.method(_interface, in_signature='b', out_signature='')
	def SetForceExcludedFlag(self, flag):
		"""sets the boolean force_excluded flag."""
		flag = bool(flag)	# since it comes in differently
		self.self.log.debug('force_excluded flag received through dbus')
		self.self.force_excluded = flag


	@dbus.service.method(_interface, in_signature='', out_signature='')
	def ResetForceExcludedFlag(self):
		"""reset the force_excluded flag."""
		self.self.log.debug('resetting force_excluded flag through dbus')
		self.self.force_excluded = None


	@dbus.service.method(_interface, in_signature='', out_signature='')
	def Quit(self):
		"""run the eva main_quit."""
		self.self.log.debug('quit received through dbus')
		self.self.main_quit()

