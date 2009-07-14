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

__all__ = ['logmeout']

SHUTDOWN_CONFIRM_DEFAULT = -1
SHUTDOWN_CONFIRM_NO = 0
SHUTDOWN_CONFIRM_YES = 1

def logmeout(mode=SHUTDOWN_CONFIRM_YES):
	"""sends a logout command through dbus to the session. this function
	works for kde 4.0, and returns after the dialog ends. (it blocks)"""

	# DOCS: http://www.purinchu.net/wp/2009/06/12/oh-fun/ (the best so far)
	# The real signature: KSMServerInterface::logout( KWorkSpace::ShutdownConfirm, KWorkSpace::ShutdownType, KWorkSpace::ShutdownMode )
	# The parameters are essentially the same as in KWorkSpace::canShutdown(), and the values are defined on that API page as well.
	# One thing to note is that the final 0 (shutdown mode) is actually useless since we're not requesting that a shutdown happen, only a logout.
	# If we were requesting a shutdown, the shutdown mode is what selects whether to force a shutdown/reboot even if other people were also logged in, for instance.
	# SOURCE: http://api.kde.org/4.x-api/kdebase-workspace-apidocs/libs/kworkspace/html/kworkspace_8h-source.html

	bus = dbus.SessionBus()
	try:
		remote_object = bus.get_object('org.kde.ksmserver', '/KSMServer')

		# specify the dbus_interface in each call
		remote_object.logout(mode, 0, -1, dbus_interface='org.kde.KSMServerInterface')

	except dbus.DBusException, e:
		return False

	return True


if __name__ == '__main__':
	logmeout()

