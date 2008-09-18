"""Tools for idle user sessions detection."""

import os

__all__ = ["sleep_until_idle"]
__author__ = "Alexandre Vassalotti <alexandre@peadrop.com>"
__version__ = "0.1"

if os.name == 'posix': from _x11_idle import _sleep_until_idle
elif os.name == 'nt': from _win32_idle import _sleep_until_idle
else: raise ImportError("operating system not supported")

def sleep_until_idle(seconds_before_idle):
	"""Pause execution until the current user session become idle.

	The given argument should be a non-integer integer representing
	the number of seconds that should elapse since the last input event
	to declare the user session as idle.
	"""
	if seconds_before_idle < 0:
		raise ValueError("argument must be non-negative")
	return _sleep_until_idle(int(seconds_before_idle))

