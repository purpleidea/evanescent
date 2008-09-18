#!/usr/bin/python

import time
import idle
from config import *			# import to globals
import exclusions
e = exclusions.exclusions(THECONFIG)
print e.is_excluded()

# kill -s ALRM <pid>
"""
import time
import os
import signal

def handler(signum, frame):
	i = 0
	while True and i < 10:
		print 'Signal handler called with signal', signum
		time.sleep(1)
		i = i + 1
		#print '*cough*, i think i caught something'
	

#signal.signal(signal.SIGALRM, handler)
signal.signal(signal.SIGALRM, signal.SIG_IGN)	# ignore

print os.getpid()
while True:

	print 'hey'
	time.sleep(3)
"""

"""

import signal
def handler(signum, frame):
    print 'Signal handler called with signal', signum
    raise IOError, "Couldn't open device!"


signal.signal(signal.SIGALRM, handler)
signal.alarm(5)		# 5 sec

try:
	signal.pause()
	print 'pause finished'
except:
	print 'exception happened!'


print 'we continue'
signal.alarm(0)          # Disable the alarm



"""



"""
import logging, logging.handlers

l = logging.getLogger('')
l.setLevel(logging.DEBUG)

# handler for local disk
class RotatingFileHandler( 	filename[, mode[, maxBytes[, backupCount]]])

# handler for global logging server
SysLogHandler = logging.handlers.SysLogHandler(('logmaster', 514))	# TODO: add a facility as a parameter here
l.addHandler(SysLogHandler)

# Now, we can log to the root logger, or any other logger. First the root...
logging.info('evanescent starting up')

daemon_logger = logging.getLogger('evanescent.daemon')
logger2 = logging.getLogger('myapp.area2')

daemon_logger.debug('Quick zephyrs blow, vexing daft Jim.')
logger1.info('How quickly daft jumping zebras vex.')
logger2.warning('Jail zesty vixen who grabbed pay from quack.')
logger2.error('The five boxing wizards jump quickly.')

"""
