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
import unittest

_ = lambda x: x			# add fake gettext function until i fix up i18n

VERBOSE = False
EXCLUDED = ['.git', 'play', 'old', 'wotd', 'tar']	# dirs to exclude
MAXSIZE = 1*1024*1024	# 1 MiB (don't let read() eat up all my memory!)

# order in which the elements should be verified.
ORDERING = ['SHEBANG', 'CODING', 'LICENSE', 'COPYRIGHT']

# set of elements that we want to match
ELEMENTS = {
	'SHEBANG': '#!/usr/bin/python',
	'CODING': '# -*- coding: utf-8 -*-',
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
	'''.replace('\t', ''),	# replace tabs used to align this text with code

	# TODO: how do we intelligently match and check the year/year range?
	# TODO: should we use fnmatch or regex or a custom match ?
	'COPYRIGHT': '''
	# Copyright (C) 2009  James Shubin, McGill University
	# Written for McGill University by James Shubin <purpleidea@gmail.com>
	#
	'''.replace('\t', ''),
}

# NOTE: line numbers for constraints are 1-based (like my text editor)
CONSTRAINTS = {
	'SHEBANG': lambda l: l['SHEBANG'] == 1,
	'CODING': lambda l: l['CODING'] == l['SHEBANG']+1,
	'LICENSE': lambda l: l['LICENSE'] > l['CODING']
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


# TODO: this test case should check the format for all .py files... DO THIS.
# TODO: maybe replace the licenseTestCase.py file with this.
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
				#XXX print 'is?: %s' % x
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
				#XXX print 'X %s' % dirname
				return True
		#XXX print 'Y %s' % dirname
		return False


	def checkFile(self, filename):
		"""checks a particular file name against all the available
		tests."""
		with open(filename, 'r') as f:
			data = f.read(MAXSIZE)

		def i2l(index, data=data):
			"""given a string; usually the output from file.read()
			and a character index, returns which the index was on.
			this function returns a 1-based number like my vim."""
			index = abs(index)
			if index >= len(data): return -1
			return len(data[0:index].split('\n'))

		location = {}
		# initialize dictionary
		for key in ORDERING: location.setdefault(i, -1)

		for key in ORDERING:
			try:
				# find the particular element inside of data
				location[key] = data.index(ELEMENTS[key])
			except ValueError, e:
				print _('%s was not found in: %s') % (key, filename)
				# XXX: would be nice to inspect constraint and
				# see what should be in it's place.
				return False

			# dictionary comprehension (build dictionary of lines)
			lines = dict([(k,i2l(v)) for k,v in location.items()])
			# check constraint
			if not CONSTRAINTS.get(key, lambda _: True)(lines):
			#if key in CONSTRAINTS and not(CONSTRAINTS[key](i2l(lines))):
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


	def XXXtestSheBang(self):
		failed = 0
		for i in self.filelist:
			with open(i, 'r') as f:
				line = f.readlines(1)[0][:-1]
				if line != ELEMENTS['SHEBANG']:
					failed = failed + 1
					print 'shebang fails at: %s' % i
					print 'shebang shown is: %s' % line
					print 'shebang model is: %s' % ELEMENTS['SHEBANG']

		if VERBOSE: print ''
		self.failUnless(failed == 0, 'one or more files failed shebang')


# group all tests into a suite
suite = unittest.TestLoader().loadTestsFromTestCase(globals()[TESTNAME])

# if this file is run individually, then run these test cases
if __name__ == '__main__':
	unittest.main()
