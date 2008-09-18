#!/usr/bin/python

# AGPLv.3
# James Shubin <purpleidea@gmail.com>
# script to find the prefix of a currently installed evanescent installation
# example: if [ `./findeva.py` ]; then echo yes; else echo no; fi
# example: x=`./findeva.py`; echo 'prefix: '$x
import sys
try:
	import evanescent.config
	print evanescent.config.prefix()
except ImportError:
	sys.exit(1)

