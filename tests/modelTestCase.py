#!/usr/bin/python
# -*- coding: utf-8 -*-
"""tests.modelTestCase

Model test case for adding tests into the automatic suite.
To add a test case:
	1) copy this file to: <xyzTestCase.py> (where `xyz' is the new name)
	2) rename the class to <xyzTestCase> (where `xyz' is the new name)
	3) modify methods in the class, building your test case
	4) edit this docstring to show the correct name and short description
	5) test by running this file. will automatically run with main suite
"""

# Copyright (C) 2009-2010  James Shubin, McGill University
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

# do some path magic so this can run anyhow from anywhere
TESTNAME = os.path.splitext(os.path.basename(os.path.normpath(__file__)))[0]
BASEPATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
sys.path.append(os.path.join(BASEPATH, 'src/'))
__all__ = [TESTNAME]


class modelTestCase(unittest.TestCase):
	"""test the dt class."""

	def setUp(self):
		"""setup code that has to occur for each test*()"""
		import datetime
		import dt
		stamp = datetime.datetime(1946, 5, 11, 3+12, 14, 15)
		self.obj = dt.dt(datetime=stamp)

	def testSimple1(self):
		self.failUnless(self.obj.is_time('[15, 16]'), 'hour range fails')

	def testSimple2(self):
		self.failUnless(self.obj.is_time('[15:00 , 15:15['), 'hour and minute range fails')

	def testSimple3(self):
		self.failUnless(self.obj.is_time('[8:00:00 , 15:14:20['), 'hour, minute and second range fails')

	def testBoundary1(self):
		self.failUnless(self.obj.is_time('[15:14:15 , 15:15:16]'), 'time doesn\'t match range 3')

# group all tests into a suite
suite = unittest.TestLoader().loadTestsFromTestCase(globals()[TESTNAME])

# if this file is run individually, then run these test cases
if __name__ == '__main__':
	unittest.main()
