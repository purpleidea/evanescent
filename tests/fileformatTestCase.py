#!/usr/bin/python
# -*- coding: utf-8 -*-
"""tests.fileformatTestCase

Test that all the files in our code distribution match a common set of aspects
and constraints. This generally tests the physical layout of the code. While
this may seem annoying, it provides an automatic lookout for small errors and
discrepancies that keep the code from otherwise being uniform and polished.
"""
# Copyright (C) 2009  James Shubin, McGill University
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
import sys
import re
import unittest

_ = lambda x: x			# add fake gettext function until i fix up i18n

VERBOSE = False
# TODO: have the excluded list along with all the ELEMENTS information in a
# separate file. it makes much more sense to keep the config info separate!
EXCLUDED = ['.git', 'play', 'old', 'wotd', 'tar']	# dirs to exclude
MAXSIZE = 1*1024*1024	# 1 MiB (don't let read() eat up all my memory!)

# order in which the elements should be verified.
ORDERING = ['SHEBANG', 'CODING', 'COPYRIGHT', 'LICENSE']

FINDTYPE_FIND = 0
FINDTYPE_INDEX = 1
FINDTYPE_RE = 2
# TODO: create a simple expression vocabulary ( * ? and | ) similar to fnmatch.
# use simple patterns and avoid complex regular expressions and escaping chars. 
# Some people, when confronted with a problem, think “I know, I'll use regular
# expressions.” Now they have two problems. --Jamie Zawinski
#FINDTYPE_FNMATCH = 3
FINDTYPE = {
	'SHEBANG': FINDTYPE_INDEX,
	'CODING': FINDTYPE_INDEX,
	'COPYRIGHT': FINDTYPE_RE,
	'LICENSE': FINDTYPE_INDEX
}

# set of elements that we want to match
ELEMENTS = {
	'SHEBANG': '#!/usr/bin/python',
	'CODING': '# -*- coding: utf-8 -*-',
	# this is a regular expression...
	'COPYRIGHT': '''
	# Copyright \(C\) (2008\-2009|2009)  James Shubin, McGill University
	# Written for McGill University by James Shubin <purpleidea@gmail.com>
	#
	'''.replace('\t', '').strip(),	# replace tabs and nl used for alignment
	'LICENSE': '''
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
	'''.replace('\t', '').strip(),
}

# NOTE: line numbers for constraints are 1-based (like my text editor)
# NOTE: input convention is (l, i) aka (line numbers, index numbers) -- each of
# which is a dictionary of tuples (start, end) indexed at the name of the rule.
CONSTRAINTS = {
	'SHEBANG': lambda l, i: l['SHEBANG'] == (1,1),
	'CODING': lambda l, i: l['CODING'][0] == l['SHEBANG'][1]+1,
	'COPYRIGHT': lambda l, i: l['COPYRIGHT'][0] >= l['CODING'][1]+1,
	'LICENSE': lambda l, i: l['LICENSE'][0] == l['COPYRIGHT'][1]+1,
}

# simple check and setup on ELEMENTS and LOCATION.
for i in ORDERING:
	if i not in ELEMENTS:
		raise AssertionError(_('Element: %s, is missing in ELEMENTS.') % i)

# do some path magic so this can run anyhow from anywhere
TESTNAME = os.path.splitext(os.path.basename(os.path.normpath(__file__)))[0]
BASEPATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
sys.path.append(os.path.join(BASEPATH, 'src/'))
__all__ = [TESTNAME]


class fileformatTestCase(unittest.TestCase):
	"""test the dt class."""

	def setUp(self):
		"""setup code that has to occur for each test*()"""

		self.filelist = []
		#dirname = dirname.rstrip('/')
		#if self.__isexcluded(dirname):
		#	return

		for (root, dirs, files) in os.walk(BASEPATH):
			remove = []
			for x in dirs:
				if self.__isexcluded(x):
					# keep track of ones we want to exclude
					remove.append(x)

			# remove all the bad ones here so as not to disrupt loop
			for x in remove:
				dirs.remove(x)

			# TODO: add exclusions ?
			for x in files:
				if os.path.splitext(x)[1] == '.py':
					self.filelist.append(os.path.join(root, x))


	def __isexcluded(self, dirname):
		"""should a directory be excluded ?"""
		# TODO: use: fnmatch.fnmatchcase ?
		for i in EXCLUDED:
			if dirname == i or dirname.endswith(i):
				return True
		return False



	def doFind(self, key, data):
		"""Match the data associated with key using its respective find
		function, to the data given as input to this function. raise an
		error if data is not found. note that if key uses FINDTYPE_FIND
		then an error will never be raised. the result will be: -1 when
		the data doesn't match. If a match succeeds return start index.
		"""
		result = None
		# how should we match in data for key
		findtype = FINDTYPE.get(key, FINDTYPE_FIND)
		pattern = ELEMENTS[key]

		# match by string find function
		if findtype == FINDTYPE_FIND:
			# this returns -1 if it doesn't find string
			where = data.find(pattern)
			result = (where, where+len(pattern))

		# match by string index function
		elif findtype == FINDTYPE_INDEX:
			try:
				# this throws error if it doesn't find string
				where = data.index(pattern)
				result = (where, where+len(pattern))
			except ValueError, e:
				result = None

		# match by regular expression
		elif findtype == FINDTYPE_RE:
			p = re.compile(pattern)
			match = p.search(data)
			if (match is not None):
				result = match.span()

		#elif findtype == FINDTYPE_FNMATCH:
		#	pass

		if result is None:
			raise ValueError(_('Key: %s not found.') % key)
		else: return result


	def checkFile(self, filename):
		"""checks a particular file name against all the available
		tests."""
		with open(filename, 'r') as f:
			data = f.read(MAXSIZE)

		# this takes the data variable (just above) as default !
		def i2l(index, data=data):
			"""given a string; usually the output from file.read()
			and a character index, returns which the index was on.
			this function returns a 1-based number like my vim."""
			if index < 0: return -1		# give what you get :P
			if index >= len(data): return -1
			return len(data[0:index].split('\n'))

		location = {}
		# initialize dictionary
		for key in ORDERING: location.setdefault(i, (-1, -1))

		for key in ORDERING:
			try:
				# find the particular element inside of data
				location[key] = self.doFind(key, data)
			except ValueError, e:
				print _('%s was not found in: %s') % (key, filename)
				# XXX: would be nice to inspect line and (then)
				# see what should be in it's place. the problem
				# is that since we don't know what the expected
				# line number should be (since this all depends
				# on the constraints) this whole ordeal is hard
				return False

			# dictionary comprehension (build dictionary of lines)
			lines = dict([(k, (i2l(v1),i2l(v2))) for k,(v1,v2) in location.items()])
			# check constraint
			if not CONSTRAINTS.get(key, lambda _: True)(lines, location):
			#if key in CONSTRAINTS and not(CONSTRAINTS[key](lines, location)):
				print _('%s failed constraint in: %s') % (key, filename)
				# XXX: would be nice to display constraint here
				print _('location table is: %s') % location
				print _('line number table is: %s') % lines
				return False

		return True


	def checkFiles(self, files, short_circuit=False):
		"""runs checkFile() on a list of files and returns an
		accumulated success or failure status."""

		result = True
		for i in files:
			if not self.checkFile(i):
				result = False
				if short_circuit: break

		return result


	def testFiles(self):
		"""test suite hook, that calls checkFiles(). this function
		depends on the setUp() function."""
		self.failUnless(
			self.checkFiles(self.filelist),
			_('Files don\'t pass format checks and constraints.')
		)


	# XXX: left as an example of what we *don't* want to do.
	#def XXXtestSheBang(self):
	#	failed = 0
	#	for i in self.filelist:
	#		with open(i, 'r') as f:
	#			line = f.readlines(1)[0][:-1]
	#			if line != ELEMENTS['SHEBANG']:
	#				failed = failed + 1
	#				print 'shebang fails at: %s' % i
	#				print 'shebang shown is: %s' % line
	#				print 'shebang model is: %s' % ELEMENTS['SHEBANG']

		if VERBOSE: print ''
		self.failUnless(failed == 0, 'one or more files failed shebang')


# group all tests into a suite
suite = unittest.TestLoader().loadTestsFromTestCase(globals()[TESTNAME])

# if this file is run individually, then run these test cases
if __name__ == '__main__':
	unittest.main()
