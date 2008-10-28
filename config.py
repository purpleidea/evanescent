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

"""some config options for the evanescent program"""
# TODO: put all these options in a config.conf.yaml file, and move it to /etc
# FIXME: change all the `from config import *' to import config, and change all
# the globals to a config.WHATEVER instead of the WHATEVER's without the class.

DEBUGMODE = False			# debug mode
WORDYMODE = True			# talk a lot (implied if debugmode is on)
IDLELIMIT = 60*60			# 1 hour before you're idle
COUNTDOWN = 10*60			# five minute countdown before shutdown
SLEEPTIME = 10*60			# poll/check computer every 10 minutes
FASTSLEEP = 1*60			# how often do we poll after the user has been warned
INITSLEEP = 15*60			# initial sleep before idle on first startup of machine
THECONFIG = '/etc/evanescent.conf.yaml'	# the config file
LOGSERVER = ('logmaster', 514)		# syslog server
DAEMONPID = '/var/run/evanescent.pid'	# pid file for daemon
MYLOGPATH = '/var/log/evanescent.log'	# path for local log file
LOGFORMAT = '%(asctime)s %(levelname)-8s %(name)-17s %(message)s'

if DEBUGMODE:				# make our debugging go faster
	IDLELIMIT = 20
	COUNTDOWN = 45
	FASTSLEEP = 10
	WORDYMODE = True

if (FASTSLEEP != 0) and (COUNTDOWN != 0) and FASTSLEEP >= COUNTDOWN:
	message = "FASTSLEEP value should be SMALLER than COUNTDOWN"
	sys.stderr.write(message + "\n")
	sys.exit(1)
