#!/usr/bin/python

import sys
import pycurl
import StringIO

print >>sys.stderr, 'Testing', pycurl.version




s = StringIO.StringIO()
c = pycurl.Curl()

c.setopt(c.URL, 'http://www.mcgill.ca/')
c.setopt(pycurl.WRITEFUNCTION, s.write)

c.perform()
c.close()

#print s.getvalue()
print s.getvalue()[0:200]	# just look at the head...

