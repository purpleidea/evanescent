#!/usr/bin/python

import yaml  
#f = open('/home/james/code/fettle/fettle.yaml')
f = open('/home/james/code/evanescent/yaml/checkME.yaml')
data = yaml.load(f)
#data = yaml.load_all(f)
#a = []
#for x in data:
#	a.append(x)
#	print x

print data
f.close()


#f = open('newtree.yaml', 'w')
#yaml.dump(data, f, default_flow_style=False)
#f.close()

import re
value = '11:22:33:44:55:66'

p = re.compile('([a-fA-F0-9]{2}[:|\-]){5}[a-fA-F0-9]')

print p.match(value)
