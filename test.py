#!/usr/bin/python
import unittest
import os
import sys

# location of the individual unit tests
TESTS = 'tests/'

# `magic' filename ending we require for test case inclusion
MAGIC = 'TestCase.py'

sys.path.append(TESTS)

suites = []

# loop through a list of valid strings we can pass to the import function
for x in [ x[0:-len('.py')] for x in os.listdir(TESTS) if x[-len(MAGIC):] == MAGIC ]:
	temp = __import__(x)
	suites.append(temp.suite)

# show the set of suites as another suite
suite = unittest.TestSuite(suites)

# if this file is run individually, then run the test suite
if __name__ == '__main__':
	unittest.TextTestRunner(verbosity=2).run(suite)

