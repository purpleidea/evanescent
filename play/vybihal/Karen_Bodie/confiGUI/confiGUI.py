#!/sr/bin/env python
#yamlyamlyaml

import sys
import yaml

try:  
	import pygtk  
	pygtk.require("2.0")  
except:  
	pass  
try:  
	import gtk  
	import gtk.glade  
except:  
	print("GTK Not Availible")
	sys.exit(1)

class confiGUI:
	"""this class parses a yaml file for display on a glade GUI"""
	
	def __init__(self):
		
		#Set the Glade file
		self.gladefile = "confiGUI.glade"  
	        self.wTree = gtk.glade.XML(self.gladefile, "mainWindow") 

		#connect our dictionary
		dic = {"on_mainWindow_destroy" : gtk.main_quit
			      , "on_exception" : self.addException
				   , "on_save" : self.fileSave
				   , "on_open" : self.fileOpen
				  , "on_clear" : self.clear
				 , "on_configSave" : self.config}
		self.wTree.signal_autoconnect(dic)
	
		#Get the Main Window, and connect the "destroy" event
		self.window = self.wTree.get_widget("mainWindow")
		if (self.window):
			self.window.connect("destroy", gtk.main_quit)

		#some variables for later
		#titles
		self.host = "Host"
		self.user = "User"
		self.date = "Date"
		self.time = "Time"
		self.fqdn = "fqdn"
		self.note = "*note*"
		self.setting = "Setting"
		self.value = "Value"
		
		#column positions
		self.chost = 0
		self.cuser = 1
		self.cdate = 2
		self.ctime = 3
		self.cfqdn = 4
		self.cnote = 5
		self.csetting = 0
		self.cvalue = 1

		#get the tree view from widget (exceptions)
		self.exceptionView = self.wTree.get_widget("exceptionView")
		#add the columns and titles to the widget
		self.addColumn(self.host, self.chost)
		self.addColumn(self.user, self.cuser)
		self.addColumn(self.date, self.cdate)
		self.addColumn(self.time, self.ctime)
		self.addColumn(self.fqdn, self.cfqdn)
		self.addColumn(self.note, self.cnote)
		
		#get the tree view from widget (config settings)
		self.configView = self.wTree.get_widget("configView")
		#add the columns and titles to the widget
		self.addColumn2(self.setting, self.csetting)
		self.addColumn2(self.value, self.cvalue)

		#create list model to use with the exceptions and attach to tree view
		self.exceptionList = gtk.ListStore(str, str, str, str, str, str)
		self.exceptionView.set_model(self.exceptionList)
		self.listy = []
		
		#create list model to use with the config settings and attach to tree view
		self.configList = gtk.ListStore(str, str)
		self.configView.set_model(self.configList)
	
		self.listofsettings=['startmeup','debugmode','wordymode','idlelimit','countdown','sleeptime','fastsleep','initsleep','tdcommand','theconfig','logserver','mylogpath','myerrpath','logformat','iconimage','readsleep','shareddir','staletime']

		#incase this is a new file, set up some blank configuration
		setup={'conf': {'idlelimit': '', 'fastsleep': '', 'readsleep': '', 'myerrpath': '', 'theconfig': '', 'staletime': '', 'initsleep': '', 'sleeptime': '', 'iconimage': '', 'logformat': '', 'logserver': '', 'shareddir': '', 'countdown': '', 'tdcommand': '', 'mylogpath': '', 'wordymode': '', 'debugmode': '', 'startmeup': ''}}
		self.listy.append(setup)
		for pie in range(0,18):
			self.configList.append([self.listofsettings[pie],self.listy[0]['conf'][self.listofsettings[pie]]])

	
	def addColumn(self, title, cID):
		"""add a column to the list view in the main app"""
		
		column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			, text=cID)
		column.set_resizable(True)
		column.set_sort_column_id(cID)
		self.exceptionView.append_column(column)

	def addColumn2(self, title, cID):
		"""add a column to the list view in the main app"""
		
		column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			, text=cID)
		column.set_resizable(True)
		column.set_sort_column_id(cID)
		self.configView.append_column(column)

	def addException(self,widget):
		"""called when user wants to add an exception"""
		exceptionDlg = exceptionDialog();
		result,newException = exceptionDlg.run()

		if (result == 0):
			"""the user clicked ok, so add this exception"""
			
			new = newException.getList()
			self.listy.append(dict([('host',new[0]),('user',new[1]),('date',new[2]),('time',new[3]),('fqdn',new[4]),('note',new[5])]))
			self.exceptionList.append(new)

	def fileSave(self,widget):
		"""called when user wants to save a file"""
		savefile = self.wTree.get_widget("entry").get_text()
		
		try:
			file = open(savefile,"w")
			
			#print our listy to the designated file in yaml format
			hold = yaml.dump(self.listy)
			file.write(hold)
			file.close()
		except IOError:
			print "Cannot write to file"
			
	def config(self,widget):
		"""called when the user changes a config setting"""
		
		llama = self.wTree.get_widget("llama").get_text()
		comboLlama = self.wTree.get_widget("comboLlama").get_active_text()
		self.listy[0]['conf'][comboLlama] = llama
		self.configList.clear()

		for pie in range(0,18):	
			
			self.configList.append([self.listofsettings[pie],self.listy[0]['conf'][self.listofsettings[pie]]])
      
	def fileOpen(self,widget):
		"""called when user wants to open a file"""
		openfile = self.wTree.get_widget("entry").get_text()	
		
		try:
			file = open(openfile,"r")
			
			data = yaml.load(file)
			file.close()
			i = len(data)
			#clear out list of exceptions for the new file
			self.listy=[]
  
			#clear the existing list in treeviews
			self.exceptionList.clear()
			self.configList.clear()

			#config settings
			self.listy.append(data[0])
			
			#find the right config settings for the display
			
			for pie in range(0,18):
				try:
					newt = data[0]['conf'][self.listofsettings[pie]]
				except(KeyError):
					newt=''
				
				self.listy[0]['conf'][self.listofsettings[pie]] = newt
				self.configList.append([self.listofsettings[pie],newt])
		
			for pong in range(1,i):
		
				try:
					r = data[pong]['host']
				except(KeyError):
					r=''
				try:
					s = data[pong]['user']
				except(KeyError):
					s=''
				try:
					t = data[pong]['date']
				except(KeyError):
					t=''
				try:
					u = data[pong]['time']
				except(KeyError):
					u=''
				try:
					v = data[pong]['fqdn']
				except(KeyError):
					v=''
				try:
					w = data[pong]['note']
				except(KeyError):
					w=''
			
				self.listy.append(dict([('host',r),('user',s),('date',t),('time',u),('fqdn',v),('note',w)]))

				#store the new values from the file in the exceptionList
				self.exceptionList.append([r,s,t,u,v,w])
				#print 'roar!'
			
		except(IOError):
			print "Cannot open file"

	def clear(self,widget):
		self.listy[1:] = []
		self.exceptionList.clear()
		
class exceptionDialog:
	"""used for add exception dialogue (exceptionDlg)"""

	def __init__(self, host="", user="", date="", time="", fqdn="", note=""):
		
		#glade setup
		self.gladefile = "confiGUI.glade"
		#return new exception setup
		self.exception = exception(host,user,date,time,fqdn,note)

	def run(self):
		"""show the pop-up dialogue box"""
		
		#load dialogue from the glade file and get widget
		self.wTree = gtk.glade.XML(self.gladefile, "exceptionDlg")
		self.dlg = self.wTree.get_widget("exceptionDlg")
		#get the entry widgets
		self.nhost = self.wTree.get_widget("nhost")
		self.nhost.set_text(self.exception.host)
		self.nuser = self.wTree.get_widget("nuser")
		self.nuser.set_text(self.exception.user)
		self.ndate = self.wTree.get_widget("ndate")
		self.ndate.set_text(self.exception.date)
		self.ntime = self.wTree.get_widget("ntime")
		self.ntime.set_text(self.exception.time)
		self.nfqdn = self.wTree.get_widget("nfqdn")
		self.nfqdn.set_text(self.exception.fqdn)
		self.nnote = self.wTree.get_widget("nnote")
		self.nnote.set_text(self.exception.note)

		#run dialogue, get response and entry values
		self.result = self.dlg.run()
		self.exception.host = self.nhost.get_text()
		self.exception.user = self.nuser.get_text()
		self.exception.date = self.ndate.get_text()
		self.exception.time = self.ntime.get_text()
		self.exception.fqdn = self.nfqdn.get_text()
		self.exception.note = self.nnote.get_text()

		#destroy the dialogue and return result and new exception
		self.dlg.destroy()
		return self.result,self.exception

class exception:
	"""represents all the exception information"""
	
	def __init__(self, host="", user="", date="", time="", fqdn="", note=""):
		
		self.host = host
		self.user = user
		self.date = date
		self.time = time
		self.fqdn = fqdn
		self.note = note

	def getList(self):
		"""returns a list of the information"""
		return [self.host, self.user, self.date, self.time, self.fqdn, self.note]

if __name__ == "__main__":
	itsGOtime = confiGUI()
	gtk.main()

	

