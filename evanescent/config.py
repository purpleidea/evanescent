#!/usr/bin/python
"""
    Evanescent machine idle detection and shutdown tool.
    Copyright (C) 2008  James Shubin, McGill University
    Written for McGill University by James Shubin <purpleidea@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys		# for sys.modules
import yamlhelp


# TODO: clean up this file and in the future add pycurl
# TODO/FIXME: maybe we should be rewriting the whole config parser module.
# make it depend on a better yamlhelp module. the idea should be that yaml_load
# opens up the yaml file. you play around with the data stored somewhere. and
# then you yaml_save and it gets stuck back into the file. no error raising or
# any mess...

#BOOTSTRAP could be a useful config file name
#import atexit
#atexit.register(del_conf)
"""
def del_conf(self):
	"" "deletes the file we downloaded" ""
	try:
		os.remove(self.file...)
	except OSError:
		# usually this happens if file doesn't exist
		return False

	return True
def load(uri):
	" ""grab a config file from a uri."" "
	# TODO...
	pass
	#return a filepath to where it is ?

"""

class config:
	"""this class does setting, manipulating, and putting to self.config
	which we ultimately use to build up the end user config info. you can
	use the self.debug option to cause debug information to be printed out
	and each function has a local debug option which can be set to override
	the global setting. each function returns bool if it did work or not."""

	def __init__(self, filename, defaults={}, expected={}, debug=False):
		self.filename = filename
		self.defaults = defaults
		self.expected = expected
		self.debug = bool(debug)
		self.config = {}


	def parse(self, key='config', debug=None):
		"""parse a yaml config file and return the conf dictionary."""
		d = (debug is None and self.debug) or debug
		result = True
		conf = yamlhelp.yamlhelp(filename=self.filename)
		try:
			data = conf.get_yaml()
		except IOError:
			# filename probably didn't exist
			result = False
			data = None

		# simple checks...
		if type(data) is dict and key in data:
			data = data[key]
		else:
			data = {}

		# convert all keys to uppercase and remove null values
		data = dict([ (key.upper(),value) for key,value in data.items() if value is not None ])

		self.config = data
		return result


	def store(self, data, key='config', debug=None):
		"""store the self.config back into file. this only writes the
		'config' dictionary key and overwrites anything else. don't use
		this for writing to the main config. this function should be
		replaced. see the TODO/FIXME comment at the top of this file."""

		d = (debug is None and self.debug) or debug

		if type(data) is not dict:
			data = {}

		data = dict([ (k.upper(),value) for k,value in data.items() if value is not None ])

		data = {key:data}

		conf = yamlhelp.yamlhelp(filename=self.filename)
		# TODO: replace the yamlhelp lib with a more clever yamlhelp lib
		try:
			conf.put_yaml(data)
		except:
			# it could raise a few different errors. who cares.
			return False

		return True


	def clean(self, debug=None):
		"""remove any values that shouldn't be present."""
		d = (debug is None and self.debug) or debug
		result = True
		badkeys = []
		for key in self.config:
			if not key in self.defaults:
				badkeys.append(key)

		# we must do this as a second loop, otherwise we get:
		# RuntimeError: dictionary changed size during iteration
		for x in badkeys:
			result = false
			del self.config[x]

		return result


	def default(self, debug=None):
		"""add any missing defaults to the dictionary."""
		d = (debug is None and self.debug) or debug
		result = True
		for key in self.defaults:
			if not key in self.config:
				result = False
				if d: print 'adding: %s' % key
				self.config[key] = self.defaults[key]

		return result


	def check(self, debug=None):
		"""wrapper for _check()."""
		if not(self._check(self.config, self.expected, debug=debug)):
			# if check fails, replace current values with defaults
			self.config = {}
			self.default(debug=False)
			return False
		return True


	def _check(self, value, expect, debug=None):
		# NOTE: this function is quality.
		"""recursively match `value' against the datatype in expect."""
		# TODO: add raising / tracing so we can find the specific error.
		d = (debug is None and self.debug) or debug

		# is expected of a specific type
		#if expect in [int, str, bool, list, tuple, dict]:
		if type(expect) is type:
			if type(value) is not expect:
				# types don't match
				if d: print 'types don\'t match'
				return False

		# descend and iterate into/over an object
		elif type(expect) in [list, tuple, dict]:
			if type(value) != type(expect):
				# wrong types
				if d: print 'wrong types'
				return False

			if len(value) != len(expect):
				# lengths don't match
				if d: print 'lengths don\'t match'
				return False

			# dict
			if type(expect) is dict:
				for k in expect:
					if not k in value:
						# missing key
						if d: print 'missing key'
						return False

					if not self._check(value[k], expect[k]):
						# recurse on dict failed
						if d: print 'dict recurse failed'
						return False

			# list or tuple
			else:
				for x in range(len(expect)):
					if not self._check(value[x], expect[x]):
						# recurse failed
						if d: print 'recurse failed'
						return False

		# call an arbitrary function
		elif type(expect) is type(lambda: True):
			if not expect(value):
				# function call failed
				if d: print 'function call failed'
				return False

		return True


	def make(self, debug=None):
		"""turn the dictionary into top level values."""
		d = (debug is None and self.debug) or debug
		for key in self.config:
			# make sure they're all uppercase
			assert key.upper() == key
			# this is the magic line. ugly but works!
			setattr(sys.modules[__name__], key, self.config[key])
			if d: print '%s =\t%s' % (key, self.config[key])

		return True


	def run(self, make=False, debug=None):
		"""do it all for a regular import."""
		d = (debug is None and self.debug) or debug
		parse = self.parse()
		if d: print 'parse: %s' % parse
		clean = self.clean()
		if d: print 'clean: %s' % clean
		default = self.default()
		if d: print 'default: %s' % default
		check = self.check()
		if d: print 'check: %s' % check
		if make:
			if d: print 'make:'
			self.make()
		else:
			if d: print 'config: %s' % self.config
			return self.config


default_config = {

	'DEBUGMODE': False,			# debug mode
	'WORDYMODE': True,			# talk a lot (implied if debugmode is on)
	# TODO: does it make sense to rename this to: THRESHOLD
	'IDLELIMIT': 60*60,			# 1 hour before you're idle
	'FASTSLEEP': 5,				# how often do we poll after the user has been warned
	'COUNTDOWN': 5*60,			# five minute countdown before shutdown
	'THECONFIG': '/etc/evanescent.conf.yaml',	# the config file
	'LOGSERVER': ['logmaster', 514],			# syslog server
	'LOGFORMAT': '%(asctime)s %(levelname)-8s %(name)-17s %(message)s',
	'MYLOGPATH': '/var/log/evanescent.log',			# path for local log file
	'UPDATEMSG': True,					# update the impending logoff msg every fastsleep or not
	'ICONIMAGE': '/usr/share/evanescent/evanescent.png',	# filename for `systray' icon


	#TODO: this option might get removed and replaced by smart polling; see: get_exclusions_changed_time
	'SLEEPTIME': 10*60				# poll/check computer every 10 minutes

}

if os.name == 'nt':
	default_config['THECONFIG'] = 'c:\WINDOWS\evanescent.conf.yaml'
	default_config['ICONIMAGE'] = '?'	# FIXME
	MYLOGPATH = 'c:\WINDOWS\system32\config\evanescent.log'


expected_types = {
	'DEBUGMODE': bool,
	'WORDYMODE': bool,
	# TODO: does it make sense to rename this to: THRESHOLD
	'IDLELIMIT': int,
	'FASTSLEEP': int,
	'COUNTDOWN': int,
	'THECONFIG': str,
	'LOGSERVER': [str, int],
	'LOGFORMAT': str,
	'MYLOGPATH': str,
	'UPDATEMSG': bool,
	'ICONIMAGE': str,

	#TODO: this option might get removed and replaced by smart polling; see: get_exclusions_changed_time
	'SLEEPTIME': int
}


obj = config(filename='/home/james/code/evanescent/files/evanescent.conf.yaml.example', defaults=default_config, expected=expected_types)

if __name__ == '__main__':
	obj.debug = True

obj.run(make=True)












"""
# default constants
STARTMEUP = True			# should evanescent run on this machine?


INITSLEEP = 15*60			# initial sleep before idle on first startup of machine
TDCOMMAND = 'shutdown -P now bye!'	# take-down command to run


DAEMONPID = '/var/run/evanescent.pid'	# pid file for daemon
MYERRPATH = '/var/log/evanescent.FAIL'	# path for FAIL log file

ICONIMAGE = 'files/evanescent.svg'	# filename for `systray' icon

SHAREDDIR = '/var/run/evanescent/'	# directory for shared evanescent/eva data


if os.name == 'nt':
	# TODO: verify these follow whatever the equivalent of a windows FHS would be.
	TDCOMMAND = 'shutdown.exe -s -t 00 -c "bye!"'

	DAEMONPID = None
	MYLOGPATH = 'c:\WINDOWS\system32\config\evanescent.log'
	MYERRPATH = 'c:\WINDOWS\system32\config\evanescent.FAIL'
	SHAREDDIR = 'c:\WINDOWS\system32\evanescent\\'

conf = yamlhelp.yamlhelp(filename=THECONFIG)
try:
	data = conf.get_yaml()
except IOError:
	# filename probably didn't exist
	data = None

if not(type(data) == type([])):
	# TODO: add a warning explaining that the config file format is bad.
	# (do this whenever we fail silently like we're doing now.)
	data = []

# remove unwanted keys and extract conf dictionary
data = [x for x in data if type(x) == type({}) and len(x) == 1 and x.has_key('conf')]

# ensure we have at least some data
if len(data) > 0 and type(data[0]) == type({}): data = data[0]['conf']
else: data = {}

# convert all keys to uppercase and remove null values
data = dict([ (key.upper(),value) for key,value in data.items() if not(value is None) ])

# TODO: convert this block into a few clever lines and a loop
if data.has_key('STARTMEUP'): STARTMEUP = bool(data['STARTMEUP'])
if data.has_key('DEBUGMODE'): DEBUGMODE = bool(data['DEBUGMODE'])
if data.has_key('WORDYMODE'): WORDYMODE = bool(data['WORDYMODE'])
if data.has_key('IDLELIMIT'): IDLELIMIT =  int(data['IDLELIMIT'])
if data.has_key('COUNTDOWN'): COUNTDOWN =  int(data['COUNTDOWN'])
if data.has_key('SLEEPTIME'): SLEEPTIME =  int(data['SLEEPTIME'])
if data.has_key('INITSLEEP'): INITSLEEP =  int(data['INITSLEEP'])
if data.has_key('TDCOMMAND'): TDCOMMAND =  str(data['TDCOMMAND'])
if data.has_key('THECONFIG'): THECONFIG =  str(data['THECONFIG'])
if data.has_key('LOGSERVER'): LOGSERVER = (str(data['LOGSERVER'])[:str(data['LOGSERVER']).find(':')], int(str(data['LOGSERVER'])[str(data['LOGSERVER']).find(':')+1:]))
if data.has_key('DAEMONPID'): DAEMONPID =  str(data['DAEMONPID'])
if data.has_key('MYLOGPATH'): MYLOGPATH =  str(data['MYLOGPATH'])
if data.has_key('MYERRPATH'): MYERRPATH =  str(data['MYERRPATH'])
if data.has_key('LOGFORMAT'): LOGFORMAT =  str(data['LOGFORMAT'])
if data.has_key('ICONIMAGE'): ICONIMAGE =  str(data['ICONIMAGE'])
if data.has_key('READSLEEP'): READSLEEP =  int(data['READSLEEP'])
if data.has_key('SHAREDDIR'): SHAREDDIR =  str(data['SHAREDDIR'])
if data.has_key('STALETIME'): STALETIME =  int(data['STALETIME'])

if DEBUGMODE:				# make our debugging go faster
	IDLELIMIT = 30
	COUNTDOWN = 45
	FASTSLEEP = 10
	INITSLEEP = 2*60		# 2 min
	WORDYMODE = True

# so that... hmmm TODO: i forget, haha.
assert not((FASTSLEEP != 0) and (COUNTDOWN != 0) and FASTSLEEP >= COUNTDOWN), 'FASTSLEEP value should be smaller than COUNTDOWN'

# so that messages don't go stale before they get a chance to be read
assert READSLEEP+FASTSLEEP < STALETIME, 'READSLEEP+FASTSLEEP should be smaller than STALETIME'
"""
