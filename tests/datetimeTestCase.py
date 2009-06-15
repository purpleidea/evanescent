import unittest

class datetimeTestCase(unittest.TestCase):
	"""test the dt class."""

	def setUp(self):
		"""setup code that has to occur for each test*()"""
		import datetime
		import sys
		sys.path.append('../')

	def testBool1(self):
		self.failUnless(bool(datetime.datetime.today()), 'datetime.datetime.today() should evaluate to True.')


# group all tests into a suite
__myname__ = __name__[__name__.rfind('.')+1:]
suite = unittest.TestLoader().loadTestsFromTestCase(globals()[__myname__])

# if this file is run individually, then run these test cases
if __name__ == '__main__':
	unittest.main()

