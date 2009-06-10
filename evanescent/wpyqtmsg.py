#!/usr/bin/python
"""
    Evanescent machine idle detection and shutdown tool.
    Copyright (C) 2008  James Shubin, McGill University
    Written for McGill University by James Shubin <purpleidea@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import time

from PyQt4.QtCore import SIGNAL as PyQt4_QtCore_SIGNAL
from PyQt4.QtGui import QApplication as PyQt4_QtGui_QApplication
from PyQt4.QtGui import QIcon as PyQt4_QtGui_QIcon
from PyQt4.QtGui import QMenu as PyQt4_QtGui_QMenu
from PyQt4.QtGui import QAction as PyQt4_QtGui_QAction ###unused?		### IF THIS IS INCLUDED THEN WE DON'T NEED TO CALL app.exec_() FOR SIGNALS AND SLOTS TO WORK (maybe?)
from PyQt4.QtGui import QSystemTrayIcon as PyQt4_QtGui_QSystemTrayIcon
from PyQt4.QtCore import QString as PyQt4_QtCore_QString
from PyQt4.QtCore import SLOT as PyQt4_QtCore_SLOT
from PyQt4.QtCore import QTimer as PyQt4_QtCore_QTimer
from PyQt4.QtCore import QObject as PyQt4_QtCore_QObject

# TODO: this is my first time using qt so please point out any newbie mistakes
# FIXME: as a result, i think a lot of this could be done better, which would fix some broken things like the tooltip

class wpyqtmsg:
	"""simple class to display messages in the system tray asynchronously.
	there are probably a lot of things broken with the way this was written.
	patches are welcome! it seems to work without causing any security issues
	and without generating any warnings. the messages will stay visible in the
	tray as long as this class isn't destroyed. aka as long as the main program
	doesn't terminate. this should be improved upon, but will suffice for now."""

	# available icons for tray
	NoIcon = PyQt4_QtGui_QSystemTrayIcon.NoIcon		#	0	No icon is shown.
	Information = PyQt4_QtGui_QSystemTrayIcon.Information	#	1	An information icon is shown.
	Warning = PyQt4_QtGui_QSystemTrayIcon.Warning		#	2	A standard warning icon is shown.
	Critical = PyQt4_QtGui_QSystemTrayIcon.Critical		#	3	A critical warning icon is shown.

	def __init__(self, icon, tooltip=None):
		# todo validate icon path, look in dlls, and etc...
		self.icon = icon
		self.tooltip = tooltip

		self.qt = {}		# keep the namespace clean and store all the qt objects in a big dictionary
		# qt startup
		self.qt['app'] = PyQt4_QtGui_QApplication(sys.argv)
		self.qt['plik'] = PyQt4_QtCore_QString(self.icon)		# tray icon image filename
		self.qt['sicon'] = PyQt4_QtGui_QIcon(self.qt['plik'])
		self.qt['tray'] = PyQt4_QtGui_QSystemTrayIcon(self.qt['sicon'])
		if type(self.tooltip) == type(''): tray.setToolTip(self.tooltip)

		# misc code shown in comments below

		#self.qt['menu'] = PyQt4_QtGui_QMenu()				###
		#self.qt['quitAction'] = self.qt['menu'].addAction('quit')	###
		#self.qt['tray'].setContextMenu(self.qt['menu'])		###

		#TODO: does this work too? self.qt['tray'].connect(self.qt['tray'], PyQt4_QtCore_SIGNAL("messageClicked()"), click)
		#PyQt4_QtCore_QObject.connect(self.qt['tray'], PyQt4_QtCore_SIGNAL("messageClicked()"), click)					#works
		#self.qt['quitAction'].connect(self.qt['quitAction'], PyQt4_QtCore_SIGNAL("triggered()"), hello)				#works
		#self.qt['quitAction'].connect(self.qt['quitAction'], PyQt4_QtCore_SIGNAL("triggered()"), app, PyQt4_QtCore_SLOT("quit()"))	#works
		#self.qt['tray'].connect(self.qt['tray'], PyQt4_QtCore_SIGNAL("activated()"), hello)
		#QtCore.QObject.connect(PyQt4_QtCore_SIGNAL("triggered()"), self.yourSlot)

		#PyQt4_QtCore_QTimer.singleShot(100, show_message, tray)
		#self.qt['tray'].showMessage("a", "Body of the message", PyQt4_QtGui_QSystemTrayIcon.Warning, 1000)
		#self.qt['tray'].showMessage("b", "Body of the message", PyQt4_QtGui_QSystemTrayIcon.Warning, 1000)

		# if you send the app.quit() signal, then this app.exec() loop exits
		# this must be called if you want the signals and slots to work
		#self.qt['app'].exec_()


	def msg(self, title, msg, icon=PyQt4_QtGui_QSystemTrayIcon.Information, secs=10):
		"""shows a message in the tray. this overwrites any message currently being displayed."""
		self.qt['tray'].show()
		# FIXME: it doesn't seem to dissapear when we ask it to. probably because we don't call app.exec_()
		self.qt['tray'].showMessage(title, msg, icon, int(secs)*1000)
		#print '%s: %s' % (title, msg)


	def hide(self):
		"""hides the tray icon and any messages currently displayed."""
		self.qt['tray'].hide()
