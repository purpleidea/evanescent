#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Dt parser for evanescent machine idle detection and shutdown tool.

Parser for the magic date & time specifications seen in the evanescent config.
This class definitely needs some love.
"""
# Copyright (C) 2008-2010  James Shubin, McGill University
# Written for McGill University by James Shubin <purpleidea@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime

COLON = ':'
COMMA = ','
LBRACKET = '['
RBRACKET = ']'

_ = lambda x: x			# add fake gettext function until i fix up i18n

class dt:
	"""class to do simple parsing of date/time strings and to tell whether they represent a valid range of now()"""
	def __init__(self, time_shift=0, datetime=None, force_brackets=False):

		self.time_shift = int(time_shift)	# do date/time calculations assuming shift of delta seconds
		self.datetime = datetime		# store a datetime class object to represent the "now"
		self.force_brackets = force_brackets

	def is_time(self, time_str):
		"""
		returns true if current time matches a time string.
		cat the following to build one:
		- open or close bracket, for inclusion or exclusion (respectively) of boundary value
		- time value>>> hour[:minute[: second]] (minutes and seconds are optional)
		- comma
		- time value as above (note: all times are in 24 hour format)
		- open or close bracket, for exclusion or inclusion (respectively) of boundary value

		* example:	[8:00:44 , 14:23[
		* example:	]9 ,5:00:23]
		* example:	9:44,12
		"""

		# add/sub the time_shift
		now = datetime.datetime.today()	# now
		if type(self.datetime) == type(now):
			now = self.datetime
		delta = datetime.timedelta(seconds=abs(self.time_shift))
		if self.time_shift < 0:
			now = now - delta
		else:
			now = now + delta

		# time range: [#:#:# , #:#:#]
		if time_str.count(COMMA) == 1:
			# assume no brackets are present until found...
			lhs_bracket = False
			rhs_bracket = False
			# default include/exclude behaviour for brackets when not specified is:
			lhs_include = True
			rhs_include = True

			if time_str[0] == LBRACKET:
				lhs_bracket = True
				lhs_include = True
			if time_str[0] == RBRACKET:
				lhs_bracket = True
				lhs_include = False

			if lhs_bracket:	# chop off left bracket
				time_str = time_str[1:]


			if time_str[-1] == LBRACKET:
				rhs_bracket = True
				rhs_include = False
			if time_str[-1] == RBRACKET:
				rhs_bracket = True
				rhs_include = True

			if rhs_bracket:	# chop off right bracket
				time_str = time_str[:-1]

			if self.force_brackets and (not(lhs_bracket) or not(rhs_bracket)):
				raise SyntaxError('missing left and right square brackets')

			# now split it up
			split = time_str.split(COMMA)

			# *** do left
			lhs = split[0].strip().split(COLON)

			# defaults
			minute = 0
			second = 0

			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(lhs) < 1 or len(lhs) > 3: raise SyntaxError("bad lhs time syntax: `%s'" % split[0].strip())

			# in case parsing int fails
			try:
				hour = int(lhs[0])
				if len(lhs) > 1: minute = int(lhs[1])
				if len(lhs) > 2: second = int(lhs[2])
			except ValueError:
				raise SyntaxError("bad lhs time value: `%s'" % split[0].strip())

			lhs_datetime = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute, second=second)


			if lhs_include:
				if not(lhs_datetime <= now):
					return False
			else:
				if not(lhs_datetime < now):
					return False

			# *** do right
			rhs = split[1].strip().split(COLON)

			# defaults
			minute = 0
			second = 0

			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(rhs) < 1 or len(rhs) > 3: raise SyntaxError("bad rhs time syntax: `%s'" % split[1].strip())

			# in case parsing int fails
			try:
				hour = int(rhs[0])
				if len(rhs) > 1: minute = int(rhs[1])
				if len(rhs) > 2: second = int(rhs[2])
			except ValueError:
				raise SyntaxError("bad rhs time value: `%s'" % split[1].strip())

			rhs_datetime = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute, second=second)

			if rhs_include:
				if not(rhs_datetime >= now):
					return False
			else:
				if not(rhs_datetime > now):
					return False

			# if it didn't fail yet, then it's good!
			return True

		elif time_str.count(COMMA) == 0:
			# TODO: add single time parsing (maybe allow 9:??:??  and 7:*    ?)
			raise NotImplementedError

		else:
			raise SyntaxError("bad time syntax: `%s'" % time_str)


	def is_date(self, date_str):
		# TODO:
		raise NotImplementedError


def is_day(days, time_shift=0):
	"""Return a boolean indicating whether or not today (with time-shift)
	is present in the passed set of days. Each day in the set is
	represented by a one character letter. Days may be specified in any
	order. If you specify a string that contains an invalid letter day
	code, then a ValueError is thrown."""
	table = {
		'Sun': 'u',
		'Mon': 'm',
		'Tue': 't',
		'Wed': 'w',
		'Thu': 'h',
		'Fri': 'f',
		'Sat': 's'}
	for i in range(len(days)):	# lowercase string or list robustly
		days[i] = days[i].lower()
	# check for valid day codes in input parameter
	for i in days:
		if not i in table.values():
			raise ValueError(_('"%s" is an invalid day code.')) % i
	# add/sub the time_shift
	now = datetime.datetime.today()	# now
	delta = datetime.timedelta(seconds=abs(time_shift))
	if time_shift < 0:
		now = now - delta
	else:
		now = now + delta

	key = now.strftime('%a')
	if key in table and table[key] in days: return True
	return False


if __name__ == '__main__':
	print 'TODO: run some test cases or do something useful here.'

