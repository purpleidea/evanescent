#!/usr/bin/python

class EError(Exception):
	"""custom exception class for evanescent related errors."""

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class DecodeError(EError):
	"""custom exception class for decode.py related errors."""

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

