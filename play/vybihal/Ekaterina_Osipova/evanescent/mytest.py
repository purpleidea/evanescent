#!/usr/bin/python

import exclusions
print "I'm running my test"
array = ['dude', 'dazzle', 'dude', 'bob']
obj=exclusions.exclusions("evanescent.conf.yaml.example")
print obj.is_excluded(array)


