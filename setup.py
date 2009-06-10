#!/usr/bin/python

import distutils.core	#from distutils.core import setup, Extension
import os
import shutil		# for copying a file
import atexit		# for deleting the copied file

NAME = 'evanescent'

# add the extension if we're going to need it
ext_modules = []
if os.name == 'posix':
	ext_modules.append(
		distutils.core.Extension('idle._x11_idle', ['idle/_x11_idle.c'], libraries = ['Xss'])
	)

data_files = []
# add the icon
data_files.append( ('share/%s' % NAME, ['files/evanescent.png']) )

# add the .yaml config file
if os.name == 'posix': shutil.copyfile('files/evanescent.conf.yaml.example', 'files/evanescent.conf.yaml')
elif os.name == 'nt': shutil.copyfile('files/evanescent.conf.yaml.wexample', 'files/evanescent.conf.yaml')
def cprm():
	"""remove the earlier copied file."""
	os.remove('files/evanescent.conf.yaml')
atexit.register(cprm)
# FIXME: it would make more sense if distutils could rename a file, this way we
# wouldn't have to change the name of the file around.
data_files.append( ('/etc/', ['files/evanescent.conf.yaml']) )

# setup
distutils.core.setup(
	name=NAME,
	version='0.1',		# FIXME version
	packages=['evanescent', 'idle'],
	package_dir={'evanescent':'evanescent'},
	ext_modules=ext_modules,
	# list of miscellaneous extra modules to include
	py_modules=['yamlhelp'],
	data_files=data_files,
	# daemon and client scripts respectively
	scripts=['evanescent.py', 'eva.py']
)

