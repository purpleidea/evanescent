#!/usr/bin/python
"""
    Wusers library for windows to replace linux `users' functionality.
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

def wps(colname=None):
	"""simple grabber function for the output of
	the windows ps.exe command that i found. you
	can specify a single column name to return a
	list containing just those column values."""
	# http://technet.microsoft.com/en-us/library/bb491010.aspx
	# TODO: use the windows supplied tasklist instead of using
	# the downloaded ps.exe the /v switch will show you users.

	o = os.popen('ps.exe -hLu', 'r')	# run the windows ps command
	a = o.readlines()			# grab all the output
	o.close()
	o = None
	if len(a) < 2: return []
	columns = a[0].split()			# list of columns (should be in order)
	if not(colname is None) and not(colname.upper() in columns): return []
	# start index of each column stored with column name as key
	sindex = dict([ (value, a[0].find(value)) for value in columns] )

	a.pop(0)				# remove first row
	values = []				# empty list of values
	for x in a:
		d = {}
		for y in columns:
			# skip over non-needed columns
			if not(colname is None) and not(y == colname.upper()): continue

			# get index
			index = columns.index(y)

			# choose start and end indices of columns text
			start = sindex[columns[index]]
			if index == len(columns)-1: end = len(x)
			else: end = sindex[columns[index+1]]+0

			# grab selection
			d[y] = x[start:end].strip()

		# add to list
		values.append(d)
	# filter chosen colname into an array, removing duplicates (list->set->list) and empty elements
	if not(colname is None): return list(set([ x[colname.upper()] for x in values if not(x[colname.upper()].strip() == '') ]))

	# otherwise return everything
	return values


if __name__ == '__main__':
	# is run from command line, we can print users
	# print out one per line, since the user names
	# that get printed out can have spaces in them
	print os.linesep.join(wps('USER'))

