"""
Re: [python-win32] NTService detecting if the Windows System is Idle

Hughes, Chad O
Fri, 10 Jun 2005 13:35:43 -0700

I think this example is what you want to do. It is not a service, but
you can turn it into one.
"""
import win32pdh
from time import sleep
import threading

pdhQuery = win32pdh.OpenQuery(None, 0)

class PDH_COUNTER_PATH_ELEMENTS(list):
  def __init__(self, l = None):
    if not l:
      l = ['127.0.0.1',None,None,None,-1,None]
    list.__init__(self,l)
    self.__machineName = self[0]
    self.__objectName = self[1]
    self.__instanceName = self[2]
    self.__parantInstance = self[3]
    self.__instanceIndex = self[4]
    self.__counterName = self[5]
  def __setMachineName(self,value):
    self.__machineName = value
    self[0] = value
  def __setObjectName(self,value):
    self.__objectName = value
    self[1] = value
  def __setInstanceName(self,value):
    self.__instanceName = value
    self[2] = value
  def __setParentInstance(self,value):
    self.__parentInstance = value
    self[3] = value
  def __setInstanceIndex(self,value):
    self.__instanceIndex = value
    self[4] = value
  def __setCounterName(self,value):
    self.__counterName = value
    self[5] = value
  def __getMachineName(self):
    return self.__machineName
  def __getObjectName(self):
    return self.__objectName
  def __getInstanceName(self):
    return self.__instanceName
  def __getParentInstance(self):
    return self.__parentInstance
  def __getInstanceIndex(self):
    return self.__instanceIndex
  def __getCounterName(self):
    return self.__counterName
  machineName = property(__getMachineName, __setMachineName)
  objectName = property(__getObjectName, __setObjectName)
  instanceName = property(__getInstanceName, __setInstanceName)
  instanceIndex = property(__getInstanceIndex, __setInstanceIndex)
  parentInstanceIndex = property(__getParentInstance,
__setParentInstance)
  counterName = property(__getCounterName, __setCounterName)
  def makeCopy(self):
    return PDH_COUNTER_PATH_ELEMENTS(self)
  def __repr__(self):
    return 'machineName = %s\nobjectName = %s\nInstanceName =%s\nparentInstance = %s\ninstanceIndex = %s\ncounterName =%s' %tuple(self)

class WorkerThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self, target = self.__runLoop)
    self.__pauseEvent = threading.Event()
    #when wait is called after clear the thread will pause until set  
    self.__pauseEvent.clear()
    self.__stayAlive = True
  def stop(self):
    self.__stayAlive = False
    #loop until runLoop is exited
    while self.isAlive():
      self.__pauseEvent.set()
  def pause(self):
    self.__pauseEvent.clear()
  def resume(self):
    self.__pauseEvent.set()
  def __runLoop(self):
    while self.__stayAlive:
      self.__pauseEvent.wait()
      #do what ever you want to do while the CPU is idle
      #example print that cpu is idle
      print 'The CPU is idle'
      

#make paths
cpe = PDH_COUNTER_PATH_ELEMENTS((
  '127.0.0.1',
  "Processor",
  '_Total', 
  None,
  -1,
  "% Idle Time"
))
#you can replace _Total with a CPU id.
#For example: replace it with 0 for the first CPU
#Look up Perfmon for more details 

procPath = win32pdh.MakeCounterPath(cpe)
procCounter = win32pdh.AddCounter(pdhQuery, procPath, 0)

#For Windows to get a good statistic you must collect once first.
#That way Windows can form a delta on the CPU usage.
win32pdh.CollectQueryData(pdhQuery)
sleep(.1)

#Lets say that the CPU is idle if it has 60% or more idle time. 
threshold = 90

worker = WorkerThread()
worker.start()
while 1:
  #type CTRL-C to stop
  try:
    #Collect the percient idle time
    win32pdh.CollectQueryData(pdhQuery) 
    format = win32pdh.PDH_FMT_LONG | win32pdh.PDH_FMT_NOSCALE
    idleTime = win32pdh.GetFormattedCounterValue(procCounter, format)[1]
    print idleTime 
    if idleTime >= threshold:
      worker.resume()
    else:
      worker.pause()
    sleep(.1)
  except:
    print 'Stopping thread'
    worker.stop()
    worker.join()
    raise


"""
Chad

-----Original Message-----
From: Animesh Bansriyar [EMAIL PROTECTED] 
Sent: Friday, June 10, 2005 12:19 PM
To: Hughes, Chad O
Subject: RE: [python-win32] NTService detecting if the Windows System is
Idle



Chad,

Thanks for the reply. What I mean here is something like say, "Google
Desktop Search". The Indexer for Google Desktop Search doesn't run until
the system is "IDLE". I am not too sure what the word IDLE means. 

On Fri, 2005-06-10 at 21:51, Hughes, Chad O wrote:
> Are you saying that you want to launch a program that waits until the 
> CPU's idle time is at a given threshold and once the threshold is met 
> the program does something until the threshold is no longer met after 
> wich your app waits for the threshold again?
> 

In my case the application uses both more memory and more CPU, hence if
the application runs throughout, the systems become slow to use. So as
you sugessted, we could have a threshold like say, the NTService runs
when the System utilizes less than 5% of the RAM and 5% of CPU. Could
you help in this regard. Does it make sense?

Thanks in Advance,
Animesh

"""
