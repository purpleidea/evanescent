#!/usr/bin/python
"""
    Exceptions for evanescent machine idle detection and shutdown tool.
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

class EError(Exception):
	"""custom exception class for evanescent related errors."""

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class DecodeError(EError):
	"""custom exception class for decode.py related errors."""

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

