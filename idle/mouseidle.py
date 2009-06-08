#!/usr/bin/python
import os

if os.name == 'posix': from _x11_idle import _mouseidle
elif os.name == 'nt': from _win32_idle import _mouseidle
else: raise ImportError("operating system not supported")

def mouseidle():
	"""Returns the number of milliseconds that the machine has been idle.
	This should work on X11 (including the DPMS bug workaround) and on
	Windows. With this function, moving the mouse resets the counter."""
	return _mouseidle()

if __name__ == '__main__':
	print mouseidle()

