#!/usr/bin/python

import sys
import PyQt4.QtCore
import PyQt4.QtGui

config_resultant = {
    'startmeup': 'True',
    'debugmode': 'False',
    'wordymode': 'True',
    'idlelimit': 3600,
    'countdown': 300,
    'sleeptime': 600,
    'fastsleep': 60,
    'initsleep': 900,
    'tdcommand': '\'shutdown -P now bye!\'',
    'theconfig': '\'/etc/evanescent.conf.yaml\'',
    'logserver': '\'logmaster:514\'',
    'daemonpid': '\'/var/run/evanescent.pid\'',
    'mylogpath': '\'/var/log/evanescent.log\'',
    'myerrpath': '\'/var/log/evanescent.FAIL\'',
    'logformat': '\'%(asctime)s %(levelname)-8s %(name)-17s %(message)s\'',
    'iconimage': '\'evanescent.png\'',
    'readsleep': 5,
    'shareddir': '\'/var/run/evanescent/\'',
    'staletime': 60 
    }

const_config_resultant = config_resultant

exclusion_resultant = {
    'host': '',
    'fqdn': '',
    'time': '',
    'user': '',
    'euid': '',
    'egid': '',
#NOT IMPLIMENTED YET
    'date': '',
    'ipv4': '',
    'ipv6': '',
    'maca': '',
#SPECIAL ?
    'conf': '',
    'note': ''
    }

const_exclusion_resultant = exclusion_resultant

config_queries = [ 
    'Load evanescent at startup [Y/n]',
    'Load evanescent in dubug mode [y/N]',
    'Load Evanescent in "wordy mode" [y/N]',
    'Set time until user is considered idle',
    'Set countdown time before shutdown',
    'Set time between system checks (while active)',
    'Set time between system checks (while idle)',
    'Set initial sleep time before system check',
    'Shutdown command',
    'Path to config file',
    'Syslog server',
    'PID file for deamon',
    'Path to log file',
    'Path to error log',
    'Log string format',
    'Icon image name',
    'Minimum sleep time between messages',
    'Path for shared eva data',
    'Time unill messages are stale' 
    ]

exception_queries = [
    'Enter host name: ',
    'Enter fully qualified domain: ',
    'Enter time range: ',
    'Enter user name: ',
    'Enter effective user ID: ',
    'Enter effective group ID: ',
#NOT IMPLIMENTED YET    
    'Enter date range: ',
    'Enter ipv4: ',
    'Enter ipv6: ',
    'Enter MAC address: ',
#SPECIAL ?
    'confconf: ',
    'notenote: '
]


class window(PyQt4.QtGui.QWidget):
    def __init__(self, parent=None):
        PyQt4.QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle("Evanescent Config")
        self.resize(475,755)
    def gen_window(self, parent):
        for i in range(0, 19):
            v = config_queries[i]
            label = PyQt4.QtGui.QLabel(v, win)
            label.move(15, 50 + 35 * i)
            label.show()
        label = PyQt4.QtGui.QLabel('Welcome to Evanescent Config', win)
        label.move(120,15)
        label.show()
        tf_cb_1 = tf_ComboBox(parent, 350, 45, 'startmeup')
        tf_cb_2 = tf_ComboBox(parent, 350, 80, 'debugmode')
        tf_cb_3 = tf_ComboBox(parent, 350, 115, 'wordymode')
        num_Box1 = numBox(parent, 350, 150, 10000, 3600, 'idlelimit')
        num_Box2 = numBox(parent, 350, 185, 10000, 300, 'countdown')
        num_Box3 = numBox(parent, 350, 220, 10000, 600, 'sleeptime')
        num_Box4 = numBox(parent, 350, 255, 10000, 60, 'fastsleep')
        num_Box5 = numBox(parent, 350, 290, 10000, 900, 'initsleep')
        text_Box1 = textBox(parent, 200, 325, 250,'shutdown -P now bye!', 'tdcommand')
        text_Box2 = textBox(parent, 200, 360, 250,'/etc/evanescent.conf.yaml', 'theconfig')
        text_Box3 = textBox(parent, 200, 395, 250,'logmaster:514', 'logserver')
        text_Box4 = textBox(parent, 200, 430, 250,'/var/run/evanescent.pid', 'daemonpid')
        text_Box5 = textBox(parent, 200, 465, 250,'/var/log/evanescent.log', 'mylogpath')
        text_Box6 = textBox(parent, 200, 500, 250,'/var/log/evanescent.FAIL', 'myerrpath')
        text_Box7 = textBox(parent, 200, 535, 250,'%(asctime)s %(levelname)-8s %(name)-17s %(message)s', 'logformat')
        text_Box8 = textBox(parent, 200, 570, 250,'evanescent.png', 'iconimage')
        num_Box6 = numBox(parent, 350, 605, 10000, 5, 'readsleep')
        text_Box9 = textBox(parent, 200, 640, 250,'/var/run/evanescent/', 'shareddir')
        num_Box7 = numBox(parent, 350, 675, 10000, 60, 'staletime')
        
        addExclusion = button(parent, 30, 715, ' Add Exclusion ', self.add_exclusion)
        writeTexit = button(parent, 185, 715, ' Write and Exit ', self.config_write)
        exitButton = button(parent, 345, 715, ' Exit ', self.exit)

        parent.show()
    
    def add_exclusion(self):    
        win.show__window(exclusion_window)

        
    def config_write(self):
        tmp_config.write("""
##########
# CONFIG #
##########
- conf:
""")
        for x in config_resultant:
            if x != '':
                tmp_config.write('\t' + str(x) + ': ' + str(config_resultant[x]) + '\n')
        self.exit()
        
    def exit(self):
        quit = PyQt4.QtGui.QPushButton('Close', self)
        self.connect(quit, PyQt4.QtCore.SIGNAL('clicked()'), PyQt4.QtGui.qApp, PyQt4.QtCore.SLOT('quit()'))
        tmp_config.write("""
#################################################
#
#                       EOF
#
#################################################""")
        tmp_config.close()
        quit.click()
        
    def gen_exclusion_window(self, parent):
        
        parent.setWindowTitle('Add Exclusion')
        parent.resize(385, 470)
        for i in range(0, 12):
            v = exception_queries[i]
            label = PyQt4.QtGui.QLabel(v, parent)
            label.move(20, 20 + 35 * i)
            label.show()
            
        textBox01 = textBox2(parent, 210, 15, 150,'host','host')
        textBox02 = textBox2(parent, 210, 50, 150,'fqdn','fqdn')
        textBox03 = textBox2(parent, 210, 85, 150,'time','time')
        textBox04 = textBox2(parent, 210, 120, 150,'user','user')
        textBox05 = textBox2(parent, 210, 155, 150,'euid','euid')
        textBox06 = textBox2(parent, 210, 190, 150,'egid','egid')
        textBox07 = textBox2(parent, 210, 225, 150,'date','date')
        textBox08 = textBox2(parent, 210, 260, 150,'ipv4','ipv4')
        textBox09 = textBox2(parent, 210, 295, 150,'ipv6','ipv6')
        textBox10 = textBox2(parent, 210, 330, 150,'maca','maca')
        textBox11 = textBox2(parent, 210, 365, 150,'conf','conf')
        textBox12 = textBox2(parent, 210, 400, 150,'note','note')
        
        exception_button1 = button(parent, 50, 435, 'Cancel', self.cancel)
        exception_button2 = button(parent, 250, 435, 'Write', self.exclusion_write)
        
    def cancel(self):
        exclusion_resultant = const_exclusion_resultant
        exclusion_window.hide()

    
    def exclusion_write(self):
        tmp_config.write("""
#############
# EXCLUSION #
#############
- """)
        for x in exclusion_resultant:
            if exclusion_resultant[x] != '':
                tmp = '' + x + ': ' + exclusion_resultant[x] + '\n  '
                tmp_config.write(tmp)
        self.cancel()


    def show__window(self, parent):
        parent.show()
        


class tf_ComboBox(PyQt4.QtGui.QComboBox):
    temp = ""
    def __init__(self, parent, xOff, yOff, target):
        PyQt4.QtGui.QComboBox.__init__(self, parent)
        self.move(xOff, yOff)
        self.addItem('Yes')
        self.addItem('No')
        self.connect(self, PyQt4.QtCore.SIGNAL('activated(int)'), self.set_var )
        self.temp = target
        self.show()
    def set_var(self, input):
        if input == 0:
            config_resultant[self.temp]='True'
        else:
            config_resultant[self.temp]='False'
 

class numBox(PyQt4.QtGui.QSpinBox):
    temp = ""
    def __init__(self, parent, xOff, yOff, max, init, target):
        PyQt4.QtGui.QSpinBox.__init__(self, parent)
        self.move(xOff, yOff)
        self.setMinimum(0)
        self.setMaximum(max)
        self.setSingleStep(1)
        self.connect(self, PyQt4.QtCore.SIGNAL('valueChanged(int)'), self.set_var )
        self.setValue(init)
        self.temp = target
        self.show()
    def set_var(self, input):
        config_resultant[self.temp] = input


class textBox(PyQt4.QtGui.QLineEdit):
    temp = ""
    def __init__(self, parent, xOff, yOff, length, init, target):
        PyQt4.QtGui.QLineEdit.__init__(self, parent)
        self.move(xOff, yOff)
        self.connect(self, PyQt4.QtCore.SIGNAL('textEdited(const QString&)'), self.set_var )
        self.setText(init)
        self.setMinimumSize(length,0)
        self.temp = target
        self.show()
    def set_var(self, input):
        config_resultant[self.temp] = '\'' + input + '\''



class textBox2(PyQt4.QtGui.QLineEdit):
    temp = ""
    def __init__(self, parent, xOff, yOff, length, init, target):
        PyQt4.QtGui.QLineEdit.__init__(self, parent)
        self.move(xOff, yOff)
        self.connect(self, PyQt4.QtCore.SIGNAL('textEdited(const QString&)'), self.set_var )
        self.setText(init)
        self.setMinimumSize(length,0)
        self.temp = target
        self.show()
    def set_var(self, input):
        exclusion_resultant[self.temp] = '' + input + ''


class button(PyQt4.QtGui.QPushButton):
    def __init__(self, parent, xOff, yOff, name, target):
        PyQt4.QtGui.QPushButton.__init__(self, parent)
        self.move(xOff, yOff)
        self.setText(name)
        self.connect(self, PyQt4.QtCore.SIGNAL('released()'), target)
        self.show()


tmp_config = open('tmp', 'w')

tmp_config.write("""#################################################
#
# This Evanescent config gile was writen using
# version 0.1 of EvaGuiConfig writen by ZEllio
# for COMP 206 in winter of 2009 at McGill
#
#################################################
""")
app = PyQt4.QtGui.QApplication(sys.argv)



win = window()
exclusion_window = window()
win.gen_window(win)
win.gen_exclusion_window(exclusion_window)
win.show__window(win)
sys.exit(app.exec_())
