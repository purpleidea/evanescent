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
# TODO: use the tempfile module with NamedTemporaryFile and delete=True
# instead of using a fixed name tempfile that is hardcoded here.this will
# only work in a new version of python. (i think it should work though)
import time
def gettempfilename():
	"""return a filename for a tempfile"""
	# FIXME: get rid of this at some point.
	# it temporary and flawed.
	return 'tempfile%s.txt' % str(time.time())

import os
import locale
import wprocess

def widle(login=None):
	"""return idle time for login or current process login if None.
	login string: 'Domain\nUser\nPassword'
		for local login use . or empty string as domain
		e.g. '.\nadministrator\nsecret_password'
	"""

	t = gettempfilename()				# get a temp file name
	out = open(t, 'w')
	wprocess.run('widle.bat', show=0, stdin=None, stdout=out, stderr=None, login=login)
	out.close()
	out = open(t, 'r')
	a = out.readlines()
	out.close()
	out = None
	os.remove(t)						# remove the tempfile
	#o = os.popen('widle.bat', 'r')		# run our script
	#a = o.readlines()					# grab all the output
	#o.close()
	#o = None
	for i in range(len(a)):				# loop
		if a[i].startswith('WIDLE'):	# find magic identifier
			if i+1 < len(a):			# does the next index exist?
				return locale.atoi(a[i+1])

	return False

