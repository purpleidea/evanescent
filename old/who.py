#!/usr/bin/python
# poor man's who

# 'ut_addr_v6', 'ut_exit',

#'ut_id',
#'ut_session',
#'ut_type', 




import utmp
import UTMPCONST

import time
import os

a = utmp.UtmpRecord()
f = "%-10s %-5s %10s %-10s %-25s %-15s %-10s %-10s %-10s %-10s %-10s"

print f % ("USER", "TTY", "PID", "HOST", "LOGIN", "IDLE", "TYPE", "SESSION", "ID", "EXIT", "IPV6")

for x in a: # example of using an iterator
	if x.ut_type == UTMPCONST.USER_PROCESS:

		tty_stats = os.stat("/dev/" + x.ut_line)
		z = time.time() - tty_stats.st_atime
		print f % (x.ut_user, x.ut_line, x.ut_pid, x.ut_host, time.ctime(x.ut_tv[0]), z, x.ut_type, x.ut_session, x.ut_id, x.ut_exit, x.ut_addr_v6)

a.endutent()	# closes the utmp file





#tty_stats = os.stat(tty)
#return time.time() - tty_stats.st_atime
