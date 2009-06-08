#!/usr/bin/python

import distutils.core	#from distutils.core import setup, Extension
import os

NAME = 'evanescent'

# build a list of modules required for setup function below
ext_modules = []
py_modules = []

py_modules.append('idle.mouseidle')
if os.name == 'posix':
	ext_modules.append(
		distutils.core.Extension('idle._x11_idle', ['idle/_x11_idle.c'], libraries = ['Xss'])
	)

if os.name == 'nt':
	py_modules.append('idle._win32_idle')

distutils.core.setup(
	name=NAME,
	version='0.1',		# FIXME version
	packages=['package', 'idle'],
	ext_modules=ext_modules,
	py_modules=py_modules,
	data_files=[('share/%s' % NAME, ['evanescent.png'])]

)

"""
......... oh!
VVVVVVVVVVVVV



data_files=[

('bitmaps', ['bm/b1.gif', 'bm/b2.gif']),

		 ('config', ['cfg/data.cfg']),

		  ('/etc/init.d', ['init-script'])

]


"""
