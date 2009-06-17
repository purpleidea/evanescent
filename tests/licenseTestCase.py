import unittest

# TODO: work on a test case that checks the formatting of each file and ensures
# that the AGPL license is at the top of each on, correctly formatted, with the
# correct copyright year, and so on. add other test cases to check for similar.
class licenseTestCase(unittest.TestCase):
	"""test the dt class."""

	def setUp(self):
		"""setup code that has to occur for each test*()"""
		import datetime
		import sys
		sys.path.append('../')
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
__myname__ = __name__[__name__.rfind('.')+1:]
suite = unittest.TestLoader().loadTestsFromTestCase(globals()[__myname__])

# if this file is run individually, then run these test cases
if __name__ == '__main__':
	unittest.main()
