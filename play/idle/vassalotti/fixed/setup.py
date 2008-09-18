#!/usr/bin/env python

import distutils.core	#from distutils.core import setup, Extension
import os

ext_modules = []
py_modules = ['mouseidle']

if os.name == 'posix':
	ext_modules.append(
		distutils.core.Extension("_x11_idle", ["_x11_idle.c"], libraries = ["Xss"])
	)

if os.name == 'nt':
	py_modules.append("_win32_idle")

distutils.core.setup(
	name="mouseidle",
	version="0.1",
	ext_modules=ext_modules,
	py_modules=py_modules
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
