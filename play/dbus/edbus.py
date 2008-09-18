#python

import dbus
import dbus.service

class DemoException(dbus.DBusException):
	_dbus_error_name = 'ca.mcgill.cs.dazzle.evanescent.eva.DemoException'


class Eva(dbus.service.Object):
	"""class for dbus eva session."""

	_interface = 'ca.mcgill.cs.dazzle.evanescent.eva.Interface'

	@dbus.service.method(_interface, in_signature='s', out_signature='as')
	def HelloWorld(self, hello_message):
		print (str(hello_message))
		#print session_bus.get_unique_name()	# FIXME: find how to get session_bus in self
		return ["Hello", " from edbus.py", "with unique name", 'could return a name here']


	@dbus.service.method(_interface, in_signature='', out_signature='')
	def RaiseException(self):
		raise DemoException('This is an exception!')


	@dbus.service.method(_interface, in_signature='', out_signature='(ss)')
	def GetTuple(self):
		return ("Hello Tuple", " from edbus.py")


	@dbus.service.method(_interface, in_signature='', out_signature='a{ss}')
	def GetDict(self):
		return {"first": "Hello Dict", "second": " from edbus.py"}


	@dbus.service.method(_interface, in_signature='', out_signature='')
	def Exit(self):
		mainloop.quit()

