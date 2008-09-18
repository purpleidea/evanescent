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


import datetime
#team awesome
DASH = '-'
COLON = ':'
COMMA = ','
LBRACKET = '['
RBRACKET = ']'

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
		now = self.__now()


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
				raise SyntaxError, 'missing left and right square brackets'

			# now split it up
			split = time_str.split(COMMA)

			# *** do left; team awesome: made it simpler
			lhs_datetime =  self.__getdt(now, split[0], COLON)


			if lhs_include:
				if not(lhs_datetime <= now):
					return False
			else:
				if not(lhs_datetime < now):
					return False

			# *** do right
			rhs_datetime = self.__getdt(now, split[1], COLON)

			if rhs_include:
				if not(rhs_datetime >= now):
					return False
			else:
				if not(rhs_datetime > now):
					return False

			# if it didn't fail yet, then it's good!
			return True



		elif time_str.count(COMMA) == 0:
			timefile=self.__getdt(now, time_str, COLON)
			#print "datefile %d-%d-%dT%d:%d:%d now %d-%d-%dT%d:%d:%d %d" % (timefile.year, timefile.month, timefile.day, timefile.hour, timefile.minute, timefile.second, now.year, now.month, now.day, now.hour, now.minute, now.second, cmp(timefile, now))
			if  timefile.hour==now.hour and timefile.minute==now.minute and timefile.second==now.second: return True
			else: return False
		else:
			raise SyntaxError, "bad time syntax: `%s'" % time_str


	# team awesome
	def is_date(self, date_str):

		now = self.__now()
		
		# date range: [yyyy-mm-dd , yyyy-mm-dd]

		if date_str.count(COMMA) == 1:
			# assume no brackets are present until found...
			lhs_bracket = False
			rhs_bracket = False
			# default include/exclude behaviour for brackets when not specified is:
			lhs_include = True
			rhs_include = True

			if date_str[0] == LBRACKET:
				lhs_bracket = True
				lhs_include = True
			if date_str[0] == RBRACKET:
				lhs_bracket = True
				lhs_include = False

			if lhs_bracket:	# chop off left bracket
				date_str =date_str[1:]

			if date_str[-1] == LBRACKET:
				rhs_bracket = True
				rhs_include = False
			if date_str[-1] == RBRACKET:
				rhs_bracket = True
				rhs_include = True

			if rhs_bracket:	# chop off right bracket
				date_str = date_str[:-1]

			if self.force_brackets and (not(lhs_bracket) or not(rhs_bracket)):
				raise SyntaxError, 'missing left and right square brackets'

			# now split it up
			split = date_str.split(COMMA)

			# do left
			lhs_datetime = self.__getdt(now, split[0], DASH)

			if lhs_include:
				if not(lhs_datetime <= now):
					return False
			else:
				if not(lhs_datetime < now):
					return False

			# do right
			rhs_datetime = self.__getdt(now, split[1], DASH)

			if rhs_include:
				if not(rhs_datetime >= now):
					return False
			else:
				if not(rhs_datetime > now):
					return False

			# if it didn't fail yet, then it's good!
			return True

		elif date_str.count(COMMA) == 0:
			datefile=self.__getdt(now, date_str, DASH)
			#print "datefile %d-%d-%dT%d:%d:%d now %d-%d-%dT%d:%d:%d %d" % (datefile.year, datefile.month, datefile.day, datefile.hour, datefile.minute, datefile.second, now.year, now.month, now.day, now.hour, now.minute, now.second, cmp(datefile, now))
			if  datefile.year==now.year and datefile.month==now.month and datefile.day==now.day: return True
			#if cmp(datefile, now, accuracy=1.0): return True
			else: return False
		else:
			raise SyntaxError, "bad date syntax: `%s'" % time_str

	#team awesome says: check for day of the week ISO-style 1=mon, 7=sun
	def weekday(self, day):
		try:
			day = int(day)
		except ValueError:
			raise SyntaxError, "bad weekday syntax: 1 is monday, 7 is sunday"
		if day < 1 or day > 7:
			raise SyntaxError, "weekday is between 1 for monday and 7 for sunday"
		now = self.__now()
		if day == now.isoweekday(): return True
		else: return False

	#team awesome says: why write this code twice?
	def __now(self):
		# add/sub the time_shift
		now = datetime.datetime.today()	# now
		if type(self.datetime) == type(now):
			now = self.datetime
		delta = datetime.timedelta(seconds=abs(self.time_shift))
		if self.time_shift < 0:
			now = now - delta
		else:
			now = now + delta
		return now

	# team awesome says: dt_str is date or time string. now is __now. sep is DASH for date or COLON for time. returns datetime.
	def __getdt(self, now, dt_str, sep):
		# split on the separator
		a = dt_str.strip().split(sep)

		# need between one and 3 chunks
		if len(a) < 1 or len(a) > 3: raise SyntaxError, "bad syntax (you suck) %s" % dt_str

		# assign
		a0 = a[0]
		if len(a) > 1: a1 = a[1]
		else:          a1 = '*'
		if len(a) > 2: a2 = a[2]
		else:          a2 = '*'
		try:
			if sep == DASH:
				# date
				if a0 == '*': year=now.year
				else: year=int(a0)
				if a1 == '*': month=now.month
				else: month=int(a1)
				if a2 == '*': day=now.day
				else: day=int(a2)
				hour   = now.hour
				minute = now.minute
				second = now.second
			elif sep == COLON:
				# time
				year = now.year
				month = now.month
				day = now.day
				if a0 == '*': hour=now.hour
				else: hour=int(a0)
				if a1 == '*': minute=now.minute
				else: minute=int(a1)
				if a2 == '*': second=now.second
				else: second=int(a2)
			else:
				raise SyntaxError, "bad separator %s" % sep
		except ValueError:
			raise SyntaxError, "bad date/time value %s" % dt_str

		#print "year %d month %d day %d hour %d minute %d second %d" % (year, month, day, hour, minute, second)
		return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)

