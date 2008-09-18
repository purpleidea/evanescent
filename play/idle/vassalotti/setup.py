#!/usr/bin/env python

# to build: $ python setup.py build_ext -i

from distutils.core import setup, Extension
import os

ext_modules = []
if os.name == 'posix':
	ext_modules.append(Extension("_x11_idle", ["_x11_idle.c"], libraries = ["Xss"]))

py_modules = ["idle"]
if os.name == 'nt':
	py_modules.append("_win32_idle")

setup(
	name="idle",
	author="Alexandre Vassalotti",
	author_email="alexandre@peadrop.com",
	description="Tools for idle user sessions detection",
	version="0.1",
	ext_modules=ext_modules,
	py_modules=py_modules
)

