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
import os
import locale

def widle():
	o = os.popen('widle.bat', 'r')		# run our script
	a = o.readlines()			# grab all the output
	o.close()
	o = None
	for i in range(len(a)):			# loop
		if a[i].startswith('WIDLE'):	# find magic identifier
			if i+1 < len(a):	# does the next index exist?
				return locale.atoi(a[i+1])

	return False

#print widle

