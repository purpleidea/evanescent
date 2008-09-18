#!/usr/bin/python

import exclusions

print "We test different users to see if they are excluded"
print "==================================================="


obj = exclusions.exclusions('evanescent.conf.yaml.example')

print """- user: joe
  date: '2008-10-11 , 2010'
  time: '[00 , 23]'
  weekdayoption: 'ON'"""


if obj.is_excluded("joe"):
	print "joe is excluded" 
else:
	print "joe is not excluded"


print """- user: Bill
  date: '2009 , 2010'
  time: '[1:*]'
  weekdayoption: 'OFF'"""


if obj.is_excluded("Bill"):
	print "Bill is excluded" 
else:
	print "Bill is not excluded"

print """- user: Paul
  date: '2009, 2010'
  time: '[0, 23:59:59]
  weekdays: 'OFF'"""
  
if obj.is_excluded("Paul"):
	print "Paul is excluded" 
else:
	print "Paul is not excluded"

print """- user: Andrew
  weekdayoption: 'ON'
  date '2009-*'"""

if obj.is_excluded("Andrew"):
	print "Andrew is excluded" 
else:
	print "Andrew is not excluded"


print """- user: Meki
  weekdayoption: 'OFF'
  time: '11:*'"""

if obj.is_excluded("Meki"):
	print "Meki is excluded" 
else:
	print "Meki is not excluded"

