#!/usr/bin/python
# -*- coding: utf-8 -*-
"""tests.datetimeTestcase

Tests some assumptions i made and expect to persist in the datetime class.
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


class datetimeTestCase(unittest.TestCase):
	"""test the dt class."""

	def setUp(self):
		"""setup code that has to occur for each test*()"""
		import datetime
		self.datetime = datetime

	def testBool1(self):
		self.failUnless(bool(self.datetime.datetime.today()), 'datetime.datetime.today() should evaluate to True.')


# group all tests into a suite
suite = unittest.TestLoader().loadTestsFromTestCase(globals()[TESTNAME])

# if this file is run individually, then run these test cases
if __name__ == '__main__':
	unittest.main()
