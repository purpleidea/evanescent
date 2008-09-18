import win32ui
from ctypes import *

class POINT(Structure):
	_fields_ = [("x", c_ulong), ("y", c_ulong)]


class Mouse:
	def __init__(self):
		self.user32 = windll.user32
		self.pt_struct = POINT()

	def GetCursorPos(self):
		'''Returns a tuple of (x,y)
		Refer to:
		http://msdn.microsoft.com/en-us/library/ms648390(VS.85).aspx
		'''
		self.user32.GetCursorPos(pointer(self.pt_struct))
		return(self.pt_struct.x, self.pt_struct.y)

	def GetPhysicalCursorPos(self):
		'''Returns a tuple of mouse positions (x, y)
		Refer To:
		http://msdn.microsoft.com/en-us/library/aa969464(VS.85).aspx
		'''
		self.user32.GetPhysicalCursorPos(pointer(self.pt_struct))
		return(self.pt_struct.x, self.pt_struct.y)

if __name__ == '__main__':

	m = Mouse()
	while True:
		print m.GetCursorPos()
