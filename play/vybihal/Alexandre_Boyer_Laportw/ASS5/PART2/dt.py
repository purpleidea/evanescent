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
COMMA = ','
LBRACKET = '['
RBRACKET = ']'
SEMICOLON = ';'
BCKSLASH = '/'

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
 		"""    is_time date checks if both date and time are null
            		if both aren't null yet time is this means that for a specific
            		date anytime is a valid exclusion
			split in is_datetime passes '' to is_time if no time is specified 
         	"""
		if time_str == '': return True


		# add/sub the time_shift
		now = datetime.datetime.today()	# now
		#if type(self.datetime) == type(now): this would reset the timedate to 2001-01-01 0:0:0
			#now = self.datetime	          did not understand the reason for this maybe to set the 
			#				   now to some inputed datetime?	
		delta = datetime.timedelta(seconds=abs(self.time_shift))
		if self.time_shift < 0:
			now = now - delta
		else:
			now = now + delta
		

 
		# time range: [hour:minute:second , hour:minute:second]
		# count commas, this will always part left hand side, 
		# if only one time specified it is assumed the exclusion goes until the next hour
		
		commas = time_str.count(COMMA)
		if commas > 1 :
			raise SyntaxError, 'bad format too many commas'
		
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

		#if there is a comma do right
		if commas == 1:
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



		elif commas == 0:
			# if no commas are present suppose it goes until the end of the hour
         		# recursive call
			hour+=1
			time_str ="%s,%d:00:00]"%(time_str, hour)
			return self.is_time(time_str)


		else:
			raise SyntaxError, "bad time syntax: `%s'" % time_str



	def is_date(self, date_str):
		"""	
			The current implementation allows the user to input an exclusion
			that repeats every year and that can overlap the new year
			example [23:12, 04:01] will set up a time period every year from 
			december 23rd to january 4th of the following year

		"""
		# same reasoning as is_time
        	if date_str == '':
            		return True

        	now =  datetime.datetime.today()
        	date = now.date
		# date range: [day:month:year , day:month:year] or simple day ex : [Monday,
		commas = date_str.count(COMMA)
		if commas > 1 :
			raise SyntaxError, 'bad format too many commas'
       		# assume no brackets are present until found...
       		lhs_bracket = False
       		rhs_bracket = True
		# default include/exclude behaviour for brackets when not specified is:
       		lhs_include = True
       		rhs_include = True

	    	if date_str[0] == LBRACKET:
	       		lhs_bracket = True
	       		lhs_include = True

	    	if date_str[0] == RBRACKET:
	       		lhs_bracket = True
	       		lhs_include = False


	    	if  lhs_bracket:
	        	date_str = date_str[1:]


	    	if date_str[-1] == LBRACKET:
	        	rhs_bracket = True
	        	rhs_include = False

	    	if date_str[-1] == RBRACKET:
	        	rhs_bracket = True
	        	rhs_include = True

	    	if rhs_bracket:
	        	date_str = date_str[:-1]



		if self.force_brackets and (not(lhs_bracket) or not(rhs_bracket)):
			raise SyntaxError, 'missing left and right square brackets'

		# now split it up
		split = date_str.split(COMMA)

		# *** do left
		lhs = split[0].strip().split(COLON)

		# defaults
		month = now.month
		# first month is used to check if the time period overlaps in the next year
		# 	example 23 of december 1999 to 4th of january 2000		
		firstmonth = 1
		year = now.year
		# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
		if len(lhs) < 1 or len(lhs) > 3: raise SyntaxError, "bad lhs date syntax: `%s'" % split[0].strip()

		# in case parsing int fails
		try:
			dayName = False
			day = int(lhs[0])
			if len(lhs) > 1:
				month = int(lhs[1])
				firstmonth = month
			if len(lhs) > 2: year = int(lhs[2])
		except ValueError:
			if(lhs[0] == 'Monday'):
				dayName = True
				leftDayNum =0
			elif(lhs[0] == 'Tuesday'):
				dayName = True
				leftDayNum =1
			elif(lhs[0] == 'Wednesday'):
				dayName = True
				leftDayNum =2
			elif(lhs[0] == 'Thursday'):
				dayName = True
				leftDayNum =3
			elif(lhs[0] == 'Friday'):
				dayName = True
				leftDayNum =4
			elif(lhs[0] == 'Saturday'):
				dayName = True
				leftDayNum =5
			elif(lhs[0] == 'Sunday'):
				dayName = True
				leftDayNum =6
			else:
				raise SyntaxError, "bad lhs date value: `%s'" % split[0].strip()
		if not dayName:
			lhs_datetime = datetime.datetime(year=year, month=month, day=day,hour=now.hour, minute=now.minute, second=now.second)

			if lhs_include:
				if not(lhs_datetime <= now):
					return False
			else:
				if not(lhs_datetime < now):
					return False
		
		if commas == 1 :			
			# *** do right
			rhs = split[1].strip().split(COLON)
			# defaults
			month = int(now.month)
			year = int(now.year)
		
			# need between one and 3 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(rhs) < 1 or len(rhs) > 3: raise SyntaxError, "bad rhs time syntax: `%s'" % split[1].strip()
			# in case parsing int fails
			try:
				rightDayNum = -1
				day = int(rhs[0])
				if len(rhs) > 1:
					month = int(rhs[1])
					firstmonth = month
				if len(rhs) > 2: year = int(lhs[2])
			except ValueError:
				if(rhs[0] == 'Monday') and dayName :
					dayName = True
					rightDayNum =0
				elif (rhs[0] == 'Tuesday') and dayName :
					dayName = True
					rightDayNum =1
				elif (rhs[0] == 'Wednesday') and dayName :
					dayName = True
					rightDayNum =2
				elif (rhs[0] == 'Thursday') and dayName:
					dayName = True
					rightDayNum =3
				elif (rhs[0] == 'Friday') and dayName :
					dayName = True
					rightDayNum =4
				elif (rhs[0] == 'Saturday') and dayName :
					dayName = True
					rightDayNum =5
				elif (rhs[0] == 'Sunday') and dayName :
					dayName = True
					rightDayNum =6
				else:
					raise SyntaxError, "bad rhs date value: `%s'" % split[0].strip()
			if not dayName:
				rhs_datetime = datetime.datetime(year=year, month=month, day= day, hour=now.hour, minute=now.minute, second=now.second)
				if rhs_include:
					if not(rhs_datetime >= now):
						return False
				else:
					if not(rhs_datetime > now):
						return False
		


			if dayName:
				nowNum = now.weekday()
				if( rightDayNum < leftDayNum ):
					rightDayNum += 7
					nowNum += 7
				if lhs_include:
					if not (leftDayNum <= nowNum):
						print 'day'
						return False
				else:
					if not (leftDayNum < nowNum):
						print 'day'
						return False	
				if rhs_include:
					if not (rightDayNum >= nowNum):
						print 'day'
						return False
				else:
					if not (rightDayNum > nowNum):
						print 'day'
						return False	

			# if it didn't fail yet, then it's good!
			return True

		elif commas == 0:
			if not dayName:
				# if no comma is present suppose it is only for one day
            			# recursive call 
  				date_str = "%s,%d:%d:%d]"%(date_str,day,month,year)
            			return self.is_date(date_str)
			if dayName:
				if(now.weekday() == leftDayNum and lhs_include):
					return True
				if(now.weekday() == leftDayNum and not lhs_include):
					return False
		else:
			raise SyntaxError, "bad date syntax: `%s'" % time_str


	def is_datetime(self, datetime_str):
		#	returns true if we are in any timespan specified under TMDT
		#	exclusion. the syntax for this exlusion is :
		#	time1/date1;time2/date2;time3;/date4; ...
		#	WARNING format does not supprot whitespace between semi-colon and arguments
		#	Dates can be passed as days of the week ex : [Monday,Friday]
	
		timespans = datetime_str.split(SEMICOLON)

		for timespan in timespans :
			if timespans == ['']: continue
			timeNdate = timespan.split(BCKSLASH)
			if len(timeNdate) < 2 :
				thedate = ''
			else:
				thedate = timeNdate[1]

			if (self.is_time(timeNdate[0]) and self.is_date(thedate)):
				return True


		#if not matched return False
		return False

