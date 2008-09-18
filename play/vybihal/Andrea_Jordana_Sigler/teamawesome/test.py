#!/usr/bin/python

import exclusions
obj = exclusions.exclusions('evanescent.conf.yaml.example')
print obj.is_excluded()
#change