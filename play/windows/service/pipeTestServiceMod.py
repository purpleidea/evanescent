# A Demo of services and named pipes.

# A multi-threaded service that simply echos back its input.

# * Install as a service using "pipeTestService.py install"
# * Use Control Panel to change the user name of the service
#   to a real user name (ie, NOT the SystemAccount)
# * Start the service.
# * Run the "pipeTestServiceClient.py" program as the client pipe side.

import win32serviceutil, win32service
#import pywintypes, win32con, winerror
# Use "import *" to keep this looking as much as a "normal" service
# as possible.  Real code shouldn't do this.
from win32event import *
from win32file import *
#from win32pipe import *
from win32api import *
from ntsecuritycon import *

# Old versions of the service framework would not let you import this
# module at the top-level.  Now you can, and can check 'Debugging()' and
# 'RunningAsService()' to check your context.
import servicemanager

class PyModTestService(win32serviceutil.ServiceFramework):
	_svc_name_ = "PyModTestService"
	_svc_display_name_ = "Python Modified Test Service"
	_svc_description_ = "Tests Python service framework by running some code."

	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.hWaitStop = CreateEvent(None, 0, 0, None)
		self.thread_handles = []

	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		SetEvent(self.hWaitStop)

	def SvcDoRun(self):
		# Write an event log record - in debug mode we will also
		# see this message printed.
		servicemanager.LogMsg(
				servicemanager.EVENTLOG_INFORMATION_TYPE,
				servicemanager.PYS_SERVICE_STARTED,
				(self._svc_name_, '')
				)

		num_connections = 0
		while 1:

		# Sleep to ensure that any new threads are in the list, and then
		# wait for all current threads to finish.
		# What is a better way?
		Sleep(500)
		# Write another event log record.
		servicemanager.LogMsg(
				servicemanager.EVENTLOG_INFORMATION_TYPE,
				servicemanager.PYS_SERVICE_STOPPED,
				(self._svc_name_, " after processing %d connections" % (num_connections,))
				)


if __name__=='__main__':
	win32serviceutil.HandleCommandLine(PyModTestService)
