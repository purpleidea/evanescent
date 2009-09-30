#!/usr/bin/python

# this man page based on information available at:
# http://www.schweikhardt.net/man_page_howto.html
# it gets generated from the template shown below.
# view this man page with: ./man.py -g | man -l -

# FIXME: write the template
template = """
"""

import os
import sys
import Cheetah.Template

__all__ = ['pyman']

class pyman:

	def __init__(self, template, namespace={}):

		#namespace = {
		#	'version': 'Hello World Example',
		#	'contents': 'Hello World!'
		#}
		self.template = template
		self.namespace = namespace

		# process template
		self.groff = Cheetah.Template.Template(template, searchList=[namespace])


	def tofile(self, filename):
		"""write groff man page output to a file."""
		try:
			f = open(filename, 'w')
			f.write(str(self.groff))
			f.close()
			return True
		except IOError, e:
			return False


	def tostdout(self):
		"""write groff output to stdout."""
		try:
			f = sys.stdout
			f.write(str(self.groff))
			f.close()
			return True
		except IOError, e:
			return False


	def main(self, argv):
		# run man with the output from the template
		if len(argv) == 1:
			if os.name == 'posix':
				os.system('./man.py -g | man -l -')
			# TODO: maybe we could add something different for windows?
			else: print 'sorry, your os cannot display man pages.'
			sys.exit()

		# write out the groff to the stdout stream
		elif len(argv) == 2 and argv[1] == '-g':
			self.tostdout()

		# write out the groff to the `evanescent.1' file
		elif len(argv) == 2 and argv[1] == '-f':
			try:
				f = open('evanescent.1', 'w')
				f.write(str(self.groff))
				f.close()
			except IOError, e:
				print e


if __name__ == '__main__':
	obj = man()
	obj.main(sys.argv)

