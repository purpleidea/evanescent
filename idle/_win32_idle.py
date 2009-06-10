import ctypes
import os
import time

if os.name != 'nt':
	raise ImportError("This modules only works with Windows 2000 or newer.")

_GetTickCount = ctypes.windll.kernel32.GetTickCount
_GetLastInputInfo = ctypes.windll.user32.GetLastInputInfo

class _LastInputInfo(ctypes.Structure):
	_fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint32)]

def _idle():
	"""returns the number of milliseconds a user is idle."""
	inputinfo = _LastInputInfo()
	inputinfo.cbSize = ctypes.sizeof(inputinfo)

	if not _GetLastInputInfo(ctypes.byref(inputinfo)):
		raise OSError("GetLastInputInfo failed")

	# number of idle milliseconds:
	return (_GetTickCount() - inputinfo.dwTime)

