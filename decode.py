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
import re
import eerror

def decode(module, nline=False):
	"""this takes a binary file that was previously encoded and stored in a
	special python file, and makes it into a real binary file again."""

	# type check
	assert (type(module) == type(''))

	# strip off a .py extension
	if module[-3:] == '.py': module = module[0:-3]

	# pull in the encoded data
	try:
		data = __import__(module)
	except ImportError:
		raise eerror.DecodeError('error importing encoded module `%s\'' % module)

	# get rid of all the newlines
	x = data.base64.replace('\n', '')

	# make it binary again
	try:
		y = base64.decodestring(x)
	except:
		raise eerror.DecodeError('error decoding `%s\' module' % module)

	# convert line endings to windows
	if nline == '\r\n':
		y = y.replace('\n', '\r\n')

		# if we did the above replace on an already
		# `windows'-ed file, then fix that here.
		while y.count('\n\n') > 0:
			y = y.replace('\n\n', '\n')

	# convert to old mac
	elif nline == '\r':
		y = y.replace('\r\n', '\r')
		y = y.replace('\n', '\r')

	# convert to linux
	elif nline == '\n':
		y = y.replace('\r\n', '\n')
		y = y.replace('\r', '\n')

	# write it out in binary
	try:
		f = open(data.filename, 'wb')
		f.write(y)
		f.close()
	except IOError:
		raise eerror.DecodeError('error writing binary file `%s\'' % data.filename)

	# return the filename used
	return data.filename


if __name__ == '__main__':
	import sys
	if len(sys.argv) != 2:
		print 'usage: %s <inputfile>' % sys.argv[0]
	else:	print decode(sys.argv[1])

