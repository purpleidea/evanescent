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
COLON = ':'
LINE = '-'
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
				raise SyntaxError, 'missing left and right square brackets'

			# now split it up
			split = time_str.split(COMMA)

			# *** do left
			lhs = split[0].strip().split(COLON)

			# defaults
			minute = 0
			second = 0

			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(lhs) < 1 or len(lhs) > 3: raise SyntaxError, "bad lhs time syntax: `%s'" % split[0].strip()

			# in case parsing int fails
			try:
				hour = int(lhs[0])
				if len(lhs) > 1: minute = int(lhs[1])
				if len(lhs) > 2: second = int(lhs[2])
			except ValueError:
				raise SyntaxError, "bad lhs time value: `%s'" % split[0].strip()

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
			if len(rhs) < 1 or len(rhs) > 3: raise SyntaxError, "bad rhs time syntax: `%s'" % split[1].strip()

			# in case parsing int fails
			try:
				hour = int(rhs[0])
				if len(rhs) > 1: minute = int(rhs[1])
				if len(rhs) > 2: second = int(rhs[2])
			except ValueError:
				raise SyntaxError, "bad rhs time value: `%s'" % split[1].strip()

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

			# *** do left
			lhs = split[0].strip().split(COLON)

			# defaults
			minute = 0
			second = 0

			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(lhs) < 1 or len(lhs) > 3: raise SyntaxError, "bad lhs time syntax: `%s'" % split[0].strip()

			# in case parsing int fails
			try:
				hourtemp = lhs[0]
				if( lhs[0] in '*'):
					hour = 0
				else:	
					hour = int(lhs[0])
					if len(lhs) > 1: 
						if (lhs[1] in '*'):
							minutes = 0
						else:
							minutes = int(lhs[1])	
							if len(lhs) > 2: 
								if(lhs[2] in '*'):
									second = 0
								else: second = int(lhs[2])
			except ValueError:
				raise SyntaxError, "bad lhs time value: `%s'" % split[0].strip()

			lhs_datetime = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute, second=second)

			#uselses stuff
			if lhs_include:
				if not(lhs_datetime <= now):
					return False
			else:
				if not(lhs_datetime < now):
					return False

			# *** do right
			rhs = split[0].strip().split(COLON)

			# defaults
			minute = 0
			second = 0

			# in case parsing int fails
			try:
				if( rhs[0] in '*'):
					hour = 23
				else:
					hour = int(rhs[0])

					if len(rhs) > 1: 
						if (rhs[1] in '*'):
							minute = 59
						else:
							minute = int(rhs[1])	
							if len(rhs) > 2: 
								if(rhs[2] in '*'):
									second = 59
								else: second = int(rhs[2])
			except ValueError:
				raise SyntaxError, "bad rhs time value: `%s'" % split[0].strip()

			rhs_datetime = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute, second=second)
			
			if rhs_include:
				if not(rhs_datetime >= now):
					return False
			else:
				if not(rhs_datetime > now):
					return False

			# if it didn't fail yet, then it's good!
			return True

		else:
			raise SyntaxError, "bad time syntax: `%s'" % time_str



	def is_date(self, date_str):
		"""
		returns true if current date matches a date string.
		cat the following to build one:
		- open or close bracket, for inclusion or exclusion (respectively) of boundary value
		- date value>>> year[-month[- day]]
		- comma
		- time value as above (note: all date are in format YEAR-MONTH-DAY)
		- open or close bracket, for exclusion or inclusion (respectively) of boundary value

		* example:	[1990-01-22 , 2009-12[
		* example:	]1 ,2009-02-23]
		* example:	]3-43 , 12]
		"""
		now = datetime.datetime.today()	# now
		if type(self.datetime) == type(now):
			now = self.datetime
		delta = datetime.timedelta(seconds=abs(self.time_shift))
		if self.time_shift < 0:
			now = now - delta
		else:
			now = now + delta

		# date range: [#-#-# , #-#-#]
		if date_str.count(COMMA) == 1:
			# now split it up
			split = date_str.split(COMMA)

			# *** do left
			lhs = split[0].strip().split(LINE)

			# defaults
			day = 1
			month = 1

			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(lhs) < 1 or len(lhs) > 3: raise SyntaxError, "bad lhs time syntax: `%s'" % split[0].strip()

			# in case parsing int fails
			try:
				year = int(lhs[0])
				if len(lhs) > 1: month = int(lhs[1])
				if len(lhs) > 2: day = int(lhs[2])
			except ValueError:
				raise SyntaxError, "bad lhs date value: `%s'" % split[0].strip()

			lhs_datetime = datetime.datetime(year=year, month=month, day=day, hour=now.hour, minute=now.minute, second=now.second)


			
			if not(lhs_datetime <= now):
				return False


			# *** do right
			rhs = split[1].strip().split(LINE)

			# defaults
			month = 12
			
			dayarray = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] 
			
			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(rhs) < 1 or len(rhs) > 3: raise SyntaxError, "bad rhs date syntax: `%s'" % split[1].strip()

			# in case parsing int fails
			try:
				year = int(rhs[0])
				if len(rhs) > 1: 
					month = int(rhs[1])
				day = dayarray[month -1]
				if len(rhs) > 2: day = int(rhs[2])
			except ValueError:
				raise SyntaxError, "bad rhs time value: `%s'" % split[1].strip()

			
	
			rhs_datetime = datetime.datetime(year=year, month=month, day=day, hour=now.hour, minute=now.minute, second=now.second+1)

			#print rhs_datetime
			#print now

			if not(rhs_datetime >= now):
					return False

			
			# if it didn't fail yet, then it's good!
			return True

		elif date_str.count(COMMA) == 0:

			# now split it up
			split = date_str.split(COMMA)

			# *** do left
			lhs = split[0].strip().split(LINE)

			# defaults
			year = 0
			month = 1
			day = 1
			dayarray = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] 
			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(lhs) < 1 or len(lhs) > 3: raise SyntaxError, "bad lhs date syntax: `%s'" % split[0].strip()

			# in case parsing int fails
			try:
				hourtemp = lhs[0]
				if( lhs[0] in '*'):
					year = 0
				else:	
					year = int(lhs[0])
					if len(lhs) > 1: 
						if (lhs[1] in '*'):
							month = 1
						else:
							month = int(lhs[1])	
							if len(lhs) > 2: 
								if(lhs[2] in '*'):
									day = 1
								else: day = int(lhs[2])
			except ValueError:
				raise SyntaxError, "bad lhs date value: `%s'" % split[0].strip()

			lhs_datetime = datetime.datetime(year=year, month=month, day=day, hour=now.hour, minute=now.minute, second=now.second)

			#uselses stuff
			
			if not(lhs_datetime <= now):
				return False

			# *** do right
			rhs = split[0].strip().split(LINE)

			# defaults
			month = 1
			day = 1

			# in case parsing int fails
			try:
				if( rhs[0] in '*'):
					year = INF
				else:
					year = int(rhs[0])

					if len(rhs) > 1: 
						if (rhs[1] in '*'):
							month = 12
						else:
							month = int(rhs[1])	
							if len(rhs) > 2: 
								if(rhs[2] in '*'):
									day = dayarray[month -1]
								else: day = int(rhs[2])
			except ValueError:
				raise SyntaxError, "bad rhs date value: `%s'" % split[0].strip()

			rhs_datetime = datetime.datetime(year=year, month=month, day=day, hour=now.hour, minute=now.minute, second=now.second+1)
			
		
			if not(rhs_datetime >= now):
					return False

			# if it didn't fail yet, then it's good!
			return True

		else:
			raise SyntaxError, "bad date syntax: `%s'" % date_str

