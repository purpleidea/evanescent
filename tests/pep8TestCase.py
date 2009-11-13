#!/usr/bin/python
# -*- coding: utf-8 -*-
"""tests.pep8TestCase

Model test case for adding tests into the automatic suite.
To add a test case:
	3) modify methods in the class, building your test case
	4) edit this docstring to show the correct name and short description
	5) test by running this file. will automatically run with main suite
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

VERBOSE = False			# print status messages
SHOW_SOURCE = False		# show source code for each error
REPEAT = False			# show all occurrences of the same error
SHOW_PEP8 = False		# show text of PEP 8 for each error

# do some path magic so this can run anyhow from anywhere, and some magic names
if __name__ == '__main__':
	TESTNAME = os.path.splitext(__file__)[0]
	if TESTNAME.startswith('./'):
		TESTNAME = TESTNAME.partition('./')[2]
	PATH = '../'	# two dots for parent
else:
	TESTNAME = __name__[__name__.rfind('.') + 1:]
	PATH = './'	# one dot for here

sys.path.append(os.path.join(PATH, 'src/'))
__all__ = [TESTNAME]


class pep8TestCase(unittest.TestCase):
	"""test the dt class."""

	def setUp(self):
		"""setup code that has to occur for each test*()"""
		import pep8
		self.pep8 = pep8	# store reference for below
		# pick options!
		options = []
		if VERBOSE: options.append('--verbose')
		if SHOW_SOURCE: options.append('--show-source')
		if REPEAT: options.append('--repeat')
		if SHOW_PEP8: options.append('--show-pep8')
		options.append('--ignore=W191,E701')
		options.append('--exclude=.git,play/')
		options.append('.')		# the '.' simulates input!
		self.pep8.process_options(options)

	def testPEP8(self):
		self.pep8.input_dir(PATH)
		self.failUnless(self.pep8.get_count() == 0, 'pep8 failed')


# group all tests into a suite
suite = unittest.TestLoader().loadTestsFromTestCase(globals()[TESTNAME])

# if this file is run individually, then run these test cases
if __name__ == '__main__':
	unittest.main()
