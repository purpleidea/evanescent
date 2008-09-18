#!/usr/bin/python
import gtk
import gio
count = 0
def file_changed(monitor, file, unknown, event):
	global count
	print 'debug: %d' % count
	count = count + 1
	print 'm: %s' % monitor
	print 'f: %s' % file
	print 'u: %s' % unknown
	print 'e: %s' % event
	if event == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
		print "file finished changing"
	print '#'*79
	print '\n'

myfile = gio.File('/tmp/gio')
monitor = myfile.monitor_file()
monitor.connect("changed", file_changed)
gtk.main()

#FILE_MONITOR_EVENT_ATTRIBUTE_CHANGED = <enum G_FILE_MONITOR_EVENT_ATTR...
#FILE_MONITOR_EVENT_CHANGED = <enum G_FILE_MONITOR_EVENT_CHANGED of typ...
#FILE_MONITOR_EVENT_CHANGES_DONE_HINT = <enum G_FILE_MONITOR_EVENT_CHAN...
#FILE_MONITOR_EVENT_CREATED = <enum G_FILE_MONITOR_EVENT_CREATED of typ...
#FILE_MONITOR_EVENT_DELETED = <enum G_FILE_MONITOR_EVENT_DELETED of typ...
#FILE_MONITOR_EVENT_PRE_UNMOUNT = <enum G_FILE_MONITOR_EVENT_PRE_UNMOUN...
#FILE_MONITOR_EVENT_UNMOUNTED = <enum G_FILE_MONITOR_EVENT_UNMOUNTED of...
#FILE_MONITOR_NONE = <flags 0 of type GFileMonitorFlags>
#FILE_MONITOR_WATCH_MOUNTS = <flags G_FILE_MONITOR_WATCH_MOUNTS of type...

