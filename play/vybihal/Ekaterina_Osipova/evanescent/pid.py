 #!/usr/bin/python

import os

if (os.system('pidof vim') == 0):
	return True
else:
	return False


