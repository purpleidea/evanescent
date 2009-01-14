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
import base64

def decode(module):
	"""this takes a binary file that was previously encoded and stored in a
	special python file, and makes it into a real binary file again."""

	# type check
	if not(type(module) == type('')): return False

	# strip off a .py extension
	if module[-3:] == '.py': module = module[0:-3]

	# pull in the encoded data
	try:
		data = __import__(module)
	except ImportError:
		return False

	# get rid of all the newlines
	x = data.base64.replace('\n', '')

	# make it binary again
	try:
		y = base64.decodestring(x)
	except:
		return False

	# write it out in binary
	try:
		f = open(data.filename, 'wb')
		f.write(y)
		f.close()
	except IOError:
		return False

	# return the filename used
	return data.filename

if __name__ == '__main__':
	import sys
	if len(sys.argv) != 2:
		print 'usage: %s <inputfile>' % sys.argv[0]
	else:	print decode(sys.argv[1])

