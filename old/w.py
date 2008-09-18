#!/usr/bin/python

#import popen2, sys
#w_stdout, w_stdin = popen2.popen2("w")
#a = w_stdin.readlines()
#a = w_stdout.readlines()
#p = subprocess.Popen(['w'], stdin=None, shell=False, stdout=subprocess.PIPE, close_fds=True)

import subprocess
import StringIO
buf = StringIO.StringIO()
p = subprocess.Popen(['w'], stdin=None, stdout=buf)
buf.rewind()
a = buf.readlines()


#a = p.stdout.readlines()
 



for x in a:
	print len(x)
	sys.stdout.write(x + "\n")
