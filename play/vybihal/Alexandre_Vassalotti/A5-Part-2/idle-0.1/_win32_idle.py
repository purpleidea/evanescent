"""Provide sleep_until_idle under Windows."""

import ctypes
import os
import time

__all__ = ["sleep_until_idle"]
__author__ = "Alexandre Vassalotti <alexandre@peadrop.com>"

if os.name != 'nt':
    raise ImportError("This modules works only with Windows 2000 or newer.")

_GetTickCount = ctypes.windll.kernel32.GetTickCount
_GetLastInputInfo = ctypes.windll.user32.GetLastInputInfo

class _LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_uint32)]

def _sleep_until_idle(seconds_before_idle):
    inputinfo = _LastInputInfo()
    inputinfo.cbSize = ctypes.sizeof(inputinfo)
    while True:
        if not _GetLastInputInfo(ctypes.byref(inputinfo)):
            raise OSError("GetLastInputInfo failed")
        idle_seconds = (_GetTickCount() - inputinfo.dwTime) / 1000
        if idle_seconds >= seconds_before_idle:
            break
        time.sleep(seconds_before_idle - idle_seconds + 1)
