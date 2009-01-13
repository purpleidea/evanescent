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
import yamlhelp

# default constants
STARTMEUP = True			# should evanescent run on this machine?
DEBUGMODE = False			# debug mode
WORDYMODE = True			# talk a lot (implied if debugmode is on)
IDLELIMIT = 60*60			# 1 hour before you're idle
COUNTDOWN = 5*60			# five minute countdown before shutdown
SLEEPTIME = 10*60			# poll/check computer every 10 minutes
FASTSLEEP = 1*60			# how often do we poll after the user has been warned
INITSLEEP = 15*60			# initial sleep before idle on first startup of machine
TDCOMMAND = 'shutdown -P now bye!'	# take-down command to run
THECONFIG = '/etc/evanescent.conf.yaml'	# the config file
LOGSERVER = ('logmaster', 514)		# syslog server
DAEMONPID = '/var/run/evanescent.pid'	# pid file for daemon
MYLOGPATH = '/var/log/evanescent.log'	# path for local log file
MYERRPATH = '/var/log/evanescent.FAIL'	# path for FAIL log file
LOGFORMAT = '%(asctime)s %(levelname)-8s %(name)-17s %(message)s'
ICONIMAGE = 'evanescent.png'		# filename for `systray' icon

if os.name in ['nt']:
	# TODO: verify these follow whatever the equivalent of a windows FHS would be.
	TDCOMMAND = 'shutdown.exe -s -t 00 -c "bye!"'
	THECONFIG = 'c:\WINDOWS\evanescent.conf.yaml'
	DAEMONPID = None
	MYLOGPATH = 'c:\WINDOWS\system32\config\evanescent.log'
	MYERRPATH = 'c:\WINDOWS\system32\config\evanescent.FAIL'

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

if DEBUGMODE:				# make our debugging go faster
	IDLELIMIT = 30
	COUNTDOWN = 45
	FASTSLEEP = 10
	INITSLEEP = 2*60		# 2 min
	WORDYMODE = True

if (FASTSLEEP != 0) and (COUNTDOWN != 0) and FASTSLEEP >= COUNTDOWN:
	import sys
	message = "FASTSLEEP value should be SMALLER than COUNTDOWN"
	sys.stderr.write(message + "\n")
	sys.exit(1)
