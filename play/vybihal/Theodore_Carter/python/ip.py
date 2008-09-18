import socket
COLON = ':'
COMMA = ','
LBRACKET = '['
RBRACKET = ']'

class ip:
	"""class to do simple parsing of date/time strings and to tell whether they represent a valid range of now()"""
	def __init__(self, force_brackets=False):
		self.force_brackets = force_brackets

	def is_ipv4(self, ip_str):
		"""
		returns true if current ip matches a ip string.
		cat the following to build one:
		- open or close bracket, for inclusion or exclusion (respectively) of boundary value
		- you can be vague
		* example:	[192.168.1.0 , 200.8[
		* example:	]192 ,5.0.23]
		* example:	9.44,12
		"""

		here = socket.gethostbyname(socket.getfqdn())	# here
		here = here.strip("'").split('.')
		here1 = int(here[0])
		here2 = int(here[1])
		here3 = int(here[2])
		part4 = int(here[3])


		# ip range: [192.168.1.0 , 192.168.1.0]
		if ip_str.count(COMMA) == 1:
			# assume no brackets are present until found...
			lhs_bracket = False
			rhs_bracket = False
			# default include/exclude behaviour for brackets when not specified is:
			lhs_include = True
			rhs_include = True

			if ip_str[0] == LBRACKET:
				lhs_bracket = True
				lhs_include = True
			if ip_str[0] == RBRACKET:
				lhs_bracket = True
				lhs_include = False

			if lhs_bracket:	# chop off left bracket
				ip_str = ip_str[1:]


			if ip_str[-1] == LBRACKET:
				rhs_bracket = True
				rhs_include = False
			if ip_str[-1] == RBRACKET:
				rhs_bracket = True
				rhs_include = True

			if rhs_bracket:	# chop off right bracket
				ip_str = ip_str[:-1]

			if self.force_brackets and (not(lhs_bracket) or not(rhs_bracket)):
				raise SyntaxError, 'missing left and right square brackets'

			# now split it up
			split = ip_str.split(COMMA)

			# *** do left
			lhs = split[0].strip().split('.')

			# defaults
			part2 = 0 
			part3 = 0
			part4 = 0

			# need between one and 4 chunks of time values to parse; eg: (x:y:z) or (x:y) or (x)
			if len(lhs) < 1 or len(lhs) > 4: raise SyntaxError, "bad lhs time syntax: `%s'" % split[0].strip()

			# in case parsing int fails
			try:
				part1 = int(lhs[0])
				if len(lhs) > 1: part2 = int(lhs[1])
				if len(lhs) > 2: part3 = int(lhs[2])
				if len(lhs) > 3: part4 = int(lhs[3])
			except ValueError:
				raise SyntaxError, "bad lhs ip value: `%s'" % split[0].strip()

			


			if not(part1<here1):
				if (part1>here1):
					return False
				if not(part2<here2):
					if (part2>here2):
						return False
					if not(part3<here3):
						if(part3>here3):
							return False
						if lhs_include:
							if not (part4<= here3):
								return False
						else:
							if not (part4< here4):
								return False


			# *** do right
			rhs = split[1].strip().split('.')

			# defaults
			part2 = 0 
			part3 = 0
			part4 = 0

			# need between one and 4 chunks of ip values to parse;
			if len(rhs) < 1 or len(rhs) > 4: raise SyntaxError, "bad rhs ip syntax: `%s'" % split[1].strip()

			# in case parsing int fails
			try:
				part1 = int(rhs[0])
				if len(rhs) > 1: part2 = int(rhs[1])
				if len(rhs) > 2: part3 = int(rhs[2])
				if len(rhs) > 3: part4 = int(rhs[3])
			except ValueError:
				raise SyntaxError, "bad rhs ip value: `%s'" % split[1].strip()
			

			if not(part1<here1):
				if (part1>here1):
					return False
				if not(part2<here2):
					if (part2>here2):
						return False
					if not(part3<here3):
						if(part3>here3):
							return False
						if rhs_include:
							if not (part4<= here3):
								return False
						else:
							if not (part4< here4):
								return False

			# if it didn't fail yet, then it's good!
			return True



		elif ip_str.count(COMMA) == 0:
			# TODO: add single ip parsing (maybe allow 9:??:??  and 7:*    ?)
			raise NotImplementedError


		else:
			raise SyntaxError, "bad time syntax: `%s'" % ip_str



    