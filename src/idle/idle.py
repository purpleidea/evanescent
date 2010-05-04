#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Idle time detection for Windows or Posix.

Returns idle time in a cross platform compatible way.
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

__all__ = ['idle', 'is_idle', 'timeleft']

if os.name == 'nt': from _win32_idle import _idle
elif os.name == 'posix':
	from _x11_idle import _idle as __idle1
	from _utmp_idle import _idle as __idle2
	_idle = lambda: min(__idle1(), __idle2())	# combine
else: raise ImportError("operating system not supported")


def idle():
	"""Returns the number of milliseconds that the machine has been idle.
	This should work on X11 (including the DPMS bug workaround) and on
	Windows. With this function, moving the mouse resets the counter.
	This also looks at each readable tty. (using utmp on posix)"""
	return _idle()


def is_idle(threshold):
	"""is the current user idle (eg: past-threshold) or not?
	threshold is specified in seconds for logical usage."""
	assert type(threshold) is int
	return idle() > int(threshold*1000)


def timeleft(threshold):
	"""return the approximate number of seconds left before the user would
	be expected to go idle, assuming no more input activity is seen."""
	assert type(threshold) is int
	return int((int(threshold*1000) - idle()) / 1000)


if __name__ == '__main__':
	print idle()

