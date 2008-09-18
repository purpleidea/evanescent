def check(value, expect):

	#if expect in [int, str, bool, list, tuple, dict]:
	if type(expect) is type:
		if type(value) is not expect:
			# types don't match
			return False

	elif type(expect) in [list, tuple, dict]:
		if type(value) != type(expect):
			# wrong types
			return False

		if len(value) != len(expect):
			# lengths don't match
			return False

		if type(expect) is dict:
			for key in expect:
				if not key in value:
					# missing key
					return False

				print expect[key]
				print value[key]
				print '$$$'
				if not check(value[key], expect[key]):
					# recurse failed
					return False

		# list or tuple
		else:
			for x in range(len(expect)):
				if not check(value[x], expect[x]):
					# recurse failed
					return False

	return True

expected = {
	'a': bool,
	'b': int,
	'c': [str, (bool, list)]
}


default = {

	'a': False,
	'b': 10*60,
	'c': ['hey', (True, {'a':5})]

}

result = check(default, expected)
print '-'*80
print result



