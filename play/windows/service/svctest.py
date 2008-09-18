import win32serviceutil, win32service, win32event

class Service(win32serviceutil.ServiceFramework):
    _svc_name_         = "jsvctest"
    _svc_display_name_ = "James Service Test"
    _svc_description_  = "This is a windows service test."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        pausetime = 60 * 1000
        while True:
            stopsignal = win32event.WaitForSingleObject(self.hWaitStop,
pausetime)
            if stopsignal == win32event.WAIT_OBJECT_0: break
            self.runOneLoop()

    def runOneLoop(self):
        import servicemanager
        servicemanager.LogInfoMsg('Jsvc is Running')



if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(Service)
