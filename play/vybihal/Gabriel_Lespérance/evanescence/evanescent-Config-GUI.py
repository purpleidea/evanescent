#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import yamlhelp

class ConfigGUI:
    
    EntryList = {}
    hasChanged = False
    
    def WriteFile(self,filename = None):
        
        if filename != None:
            self.filename = filename
        
        yamlwrapper = yamlhelp.yamlhelp(self.filename)
        yamlwrapper.put_yaml(self.data)
        self.hasChanged = False
    
    def OpenFile(self,filename = "./evanescent.conf.yaml.example" ):
        
        
        self.filename = filename
        yamlwrapper = yamlhelp.yamlhelp(filename=self.filename)
        
        self.data = yamlwrapper.get_yaml()
        
        if not(type(self.data) == type([])):
            return                              #TODO: Print out a dialog to warn the user...
        
        #taken from config.py
        # convert all keys to uppercase and remove null values
        self.data[0]['conf'] = dict([ (key.upper(),value) for key,value in self.data[0]['conf'].items() if not(value is None) ])
        
        if self.data[0]['conf'].has_key('STARTMEUP'): self.EntryList['STARTMEUP'].set_text(str(self.data[0]['conf']['STARTMEUP']))
        if self.data[0]['conf'].has_key('DEBUGMODE'): self.EntryList['DEBUGMODE'].set_text(str(self.data[0]['conf']['DEBUGMODE']))
        if self.data[0]['conf'].has_key('WORDYMODE'): self.EntryList['WORDYMODE'].set_text(str(self.data[0]['conf']['WORDYMODE']))
        if self.data[0]['conf'].has_key('IDLELIMIT'): self.EntryList['IDLELIMIT'].set_text(str(self.data[0]['conf']['IDLELIMIT']))
        if self.data[0]['conf'].has_key('COUNTDOWN'): self.EntryList['COUNTDOWN'].set_text(str(self.data[0]['conf']['COUNTDOWN']))
        if self.data[0]['conf'].has_key('SLEEPTIME'): self.EntryList['SLEEPTIME'].set_text(str(self.data[0]['conf']['SLEEPTIME']))
        if self.data[0]['conf'].has_key('INITSLEEP'): self.EntryList['INITSLEEP'].set_text(str(self.data[0]['conf']['INITSLEEP']))
        if self.data[0]['conf'].has_key('TDCOMMAND'): self.EntryList['TDCOMMAND'].set_text(str(self.data[0]['conf']['TDCOMMAND']))
        if self.data[0]['conf'].has_key('LOGSERVER'): self.EntryList['LOGSERVER'].set_text(str(self.data[0]['conf']['LOGSERVER']))
        if self.data[0]['conf'].has_key('DAEMONPID'): self.EntryList['DAEMONPID'].set_text(str(self.data[0]['conf']['DAEMONPID']))
        if self.data[0]['conf'].has_key('MYLOGPATH'): self.EntryList['MYLOGPATH'].set_text(str(self.data[0]['conf']['MYLOGPATH']))
        if self.data[0]['conf'].has_key('MYERRPATH'): self.EntryList['MYERRPATH'].set_text(str(self.data[0]['conf']['MYERRPATH']))
        if self.data[0]['conf'].has_key('LOGFORMAT'): self.EntryList['LOGFORMAT'].set_text(str(self.data[0]['conf']['LOGFORMAT']))
        if self.data[0]['conf'].has_key('ICONIMAGE'): self.EntryList['ICONIMAGE'].set_text(str(self.data[0]['conf']['ICONIMAGE']))
        if self.data[0]['conf'].has_key('READSLEEP'): self.EntryList['READSLEEP'].set_text(str(self.data[0]['conf']['READSLEEP']))
        if self.data[0]['conf'].has_key('SHAREDDIR'): self.EntryList['SHAREDDIR'].set_text(str(self.data[0]['conf']['SHAREDDIR']))
        if self.data[0]['conf'].has_key('STALETIME'): self.EntryList['STALETIME'].set_text(str(self.data[0]['conf']['STALETIME']))
        if self.data[0]['conf'].has_key('FASTSLEEP'): self.EntryList['FASTSLEEP'].set_text(str(self.data[0]['conf']['FASTSLEEP']))
        
        self.hasChanged = False
    
    def OpenFileWrapper(self, w):
        self.OpenFile(self.filew.get_filename())
        self.filew.destroy()
        
    def WriteFileWrapper(self, w):
        self.WriteFile(self.filew.get_filename())
        self.filew.destroy()
    
    def FileDialog(self, ok_callback):
         # Create a new file selection widget
        self.filew = gtk.FileSelection("File selection")

        self.filew.connect("destroy", self.filew.destroy)
        # Connect the ok_button to file_ok_sel method
        self.filew.ok_button.connect("clicked", ok_callback)
    
        # Connect the cancel_button to destroy the widget
        self.filew.cancel_button.connect("clicked", self.filew.destroy)
    
        self.filew.show()
        return
    
    def menuitem_response(self, cmd):
        if cmd == "file.open":
            if self.hasChanged == True:
                self.AskSaveFileDialog(self.SaveForOpenCallBack)
            else:
                self.FileDialog(self.OpenFileWrapper)
        elif cmd == "file.save":
            self.WriteFile()
        elif cmd == "file.saveAs":
            self.FileDialog(self.WriteFileWrapper)

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        
        if self.hasChanged == True:
            self.AskSaveFileDialog(self.QuitDialogCallBack)
            return True
        return False
    def SaveForOpenCallBack(self, response):
        self.dialog.destroy()
        if response == "yes":
            self.WriteFile()
        self.FileDialog(self.OpenFileWrapper)
        
    def QuitDialogCallBack(self,response):
        
        if response == "yes":
            self.WriteFile()
        
        self.QuitApp()
        
        
    def QuitApp(self):
        gtk.main_quit()
    
    def AskSaveFileDialog(self, callback):
       print "QuitDialog()"
       self.dialog = gtk.Dialog("Save before quitting?",
                     self.window,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
       
       label = gtk.Label("The configuration file has been modified.\nSave changes?")
       label.set_justify(gtk.JUSTIFY_CENTER)
       label.set_line_wrap(True)
       
       self.dialog.vbox.pack_start(label, True, True, 20)
       
       yes_button = gtk.Button(None,gtk.STOCK_YES)
       yes_button.connect_object("clicked", callback, "yes")
       yes_button.show()
       self.dialog.action_area.pack_start(yes_button, True, True, 0)

       
       no_button = gtk.Button(None, gtk.STOCK_NO)
       no_button.connect_object("clicked", callback, "no")
       no_button.show()
       self.dialog.action_area.pack_start(no_button, True, True, 0)
       
       cancel_button = gtk.Button(None, gtk.STOCK_CANCEL)
       cancel_button.connect("clicked", lambda w: self.dialog.destroy())
       
       cancel_button.show()
       self.dialog.action_area.pack_start(cancel_button, True, True, 0)
       
       label.show()
       self.dialog.show()
       
    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        
        if self.hasChanged == True:
            self.AskSaveFileDialog(self.QuitDialogCallBack)
            return
        
        self.QuitApp()
    
    def VarChanged(self, entry, VarName):
        #print VarName + ": " + entry.get_text()
        self.hasChanged = True     
        self.data[0]['conf'][VarName] = entry.get_text()
    
    def create_var_box(self, varname, comment = None):
        #print("Creating var_box for " + varname)
        main_box =  gtk.VBox(False,0)
        main_box.show()
        
        var_box = gtk.HBox(False,0)
        var_box.show()
        
        varNameLbl = gtk.Label("<b>" + varname + " :</b>")
        varNameLbl.set_use_markup(True)
        varNameLbl.show()
        
        
        entry = gtk.Entry(255)
        entry.show()
        entry.set_editable(True)
        entry.connect("changed", self.VarChanged, varname)
        
        self.EntryList[varname] = entry
        
        var_box.pack_start(varNameLbl, False, False,10)
        var_box.pack_start(entry, True, True,10)
        
        main_box.pack_start(var_box,False,False, 5)
                            
        if comment != None:
            commentbox = gtk.HBox(False,0)
            commentbox.show()
            
            commentLbl = gtk.Label("<i>" + comment + "</i>")
            commentLbl.show()
            commentLbl.set_use_markup(True)
            commentLbl.set_line_wrap(True)
            
            commentbox.pack_start(commentLbl,False,False,10)
            
            main_box.pack_start(commentbox,False,False,5)
        
        
        return main_box
     
        
    def create_window_layout(self):
        main_box = gtk.HBox(False,10)
        main_box.show()
        
        left_section_frame = gtk.Frame()
        left_section_frame.show()
        left_section_box = gtk.VBox(False,0)
        left_section_box.show()

        # create a new scrolled window.
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        
        scrolled_window.show()
        
        right_section_frame = gtk.Frame()
        right_section_frame.show()
        
        right_var_box = gtk.VBox(False,0)
        right_var_box.show()
        
        scrolled_window.add_with_viewport(right_var_box)
        
        right_section_frame.add(scrolled_window)
        right_section_frame.set_size_request(500, 600)
        
        ###
        # Var addition NOTE: this should be done more clearly & with a loop...
        
        newVar = self.create_var_box("STARTMEUP", "should evanescent run on this machine?")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("DEBUGMODE", "Debug Mode")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("WORDYMODE", "talk a lot (implied if debugmode is on)")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("IDLELIMIT", "Amount of time for a user to be considered idle. (in seconds)")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("COUNTDOWN", "Countdown before shutdown. (in seconds)")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("SLEEPTIME", "Poll/check computer every n seconds.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("FASTSLEEP", "How often do we poll after the user has been warned.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("INITSLEEP", "Initial sleep before idle on first startup of machine.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("TDCOMMAND", "Take-down command to run")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("LOGSERVER", "Syslog server.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("DAEMONPID", "Pid file for daemon.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("MYLOGPATH", "Path for local log file.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("MYERRPATH", "Path for FAIL log file.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("LOGFORMAT", None)
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("ICONIMAGE", "Filename for 'systray' icon.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("READSLEEP", "Minimum sleep time between messages.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("SHAREDDIR", "Directory for shared evanescent/eva data.")
        right_var_box.pack_start(newVar, True,True,5)
        
        newVar = self.create_var_box("STALETIME", "Time limit before widle or msg data considered stale.")
        right_var_box.pack_start(newVar, True,True,5)
        
        main_box.pack_start(left_section_frame, False, False, 0)
        main_box.pack_start(right_section_frame, False, False, 0)
        
        return main_box
        

    def __init__(self):
        # create a new window
        main_box = gtk.VBox(False,10)
        main_box.show()
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
    
        self.window.set_border_width(0)
        
        menu_bar = gtk.MenuBar()
        main_box.pack_start(menu_bar,False,False,0)
        menu_bar.show()
        
        file_item = gtk.MenuItem("File")
        file_item.show()

        file_menu = gtk.Menu()
        file_menu.show()
        
        open_item = gtk.MenuItem("Open")
        save_item = gtk.MenuItem("Save")
        saveAs_item = gtk.MenuItem("Save As")
        quit_item = gtk.MenuItem("Quit")
        
        file_menu.append(open_item)
        file_menu.append(save_item)
        file_menu.append(saveAs_item)
        file_menu.append(quit_item)
        
        open_item.show()
        save_item.show()
        saveAs_item.show()
        quit_item.show()
        
        file_item.set_submenu(file_menu)
        menu_bar.append(file_item)
        
        open_item.connect_object("activate", self.menuitem_response, "file.open")
        save_item.connect_object("activate", self.menuitem_response, "file.save")
        saveAs_item.connect_object("activate", self.menuitem_response, "file.saveAs")
        quit_item.connect_object ("activate", self.destroy, "file.quit")
        
        content = self.create_window_layout()
        main_box.pack_start(content, False,False,0)
        
        self.window.add(main_box)
        
        # and the window
        self.window.show()
        
        self.OpenFile()

    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it


if __name__ == "__main__":
    cfgGUI = ConfigGUI()
    cfgGUI.main()