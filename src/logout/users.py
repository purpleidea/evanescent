#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Users detection and listing.

Lists the current users on a particular machine.
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

_ = lambda x: x			# add fake gettext function until i fix up i18n

__all__ = ['ls', 'exist']

if os.name == 'nt':
	from _wts import lsusers as __lsusers
	def ls():
		"""return the list of users on the machine."""
		# TODO: should we filter by session?
		# FIXME: should we exclude blank usernames? what do they mean?
		return [x.username for x in __lsusers() if x.username != '']

elif os.name == 'posix':
	import utmp
	import UTMPCONST			# for utmp constants

	def ls():
		"""return the list of users on the machine."""
		f = UTMPCONST.USER_PROCESS	# filter for
		u = utmp.UtmpRecord()		# iterator
		users = [x.ut_user for x in u if x.ut_type == f]
		u.endutent()			# close the utmp file!
		return users

else: raise ImportError("operating system not supported")


def exist():
	"""is there at least one person using the machine?"""
	return len(ls()) > 0


if __name__ == '__main__':
	import sys
	if len(sys.argv) == 2 and sys.argv[1] in __all__:

		if sys.argv[1] == 'ls': print ls()
		elif sys.argv[1] == 'exist': print exist()

	else: print 'usage: %s ls | exist' % sys.argv[0]

