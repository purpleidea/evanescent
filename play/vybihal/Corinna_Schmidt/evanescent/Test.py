#!/usr/bin/python
#Script to test if exclusions.py & dt.py are working properly

import sys
import exclusions
import dt
import evanescent
import yaml

#var=0
#import socket
#s = socket.gethostbyname(socket.gethostname())
#print s

obj=exclusions.exclusions("yaml")

temp = dt.dt(time_shift=obj.time_shift)
print obj.is_excluded("daine")

