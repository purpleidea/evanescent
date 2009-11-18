#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Idle time detection for Windows.

Returns idle time on Windows. Meant to be called by a higher level wrapper.
"""
# Copyright (C) 2008-2009  James Shubin, McGill University
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

# Based 99% on code and help from Alexandre Vassalotti <alexandre@peadrop.com>

import os
if os.name != 'nt':
	raise ImportError("This modules requires Windows 2000 or newer.")
import ctypes
import time

__all__ = ['_idle']

_GetTickCount = ctypes.windll.kernel32.GetTickCount
_GetLastInputInfo = ctypes.windll.user32.GetLastInputInfo

class _LastInputInfo(ctypes.Structure):
	_fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint32)]

def _idle():
	"""returns the number of milliseconds a user is idle."""
	inputinfo = _LastInputInfo()
	inputinfo.cbSize = ctypes.sizeof(inputinfo)

	if not _GetLastInputInfo(ctypes.byref(inputinfo)):
		raise OSError("GetLastInputInfo failed")

	# number of idle milliseconds:
	return (_GetTickCount() - inputinfo.dwTime)


if __name__ == '__main__':
	print _idle()

