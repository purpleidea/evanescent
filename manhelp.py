#!/usr/bin/python
# -*- coding: utf-8 -*-

# NOTE: a useful guide to actually writing man pages can be found at:
# http://www.schweikhardt.net/man_page_howto.html
# NOTE: nroff man page output can be viewed by piping it to man like this:
# ./<generate_nroff> | man -l -
# TODO: manhelp could be extended to aid in actually generating nroff, e.g.:
# http://andialbrecht.wordpress.com/2009/03/17/creating-a-man-page-with-distutils-and-optparse/

import os
import sys
import gzip
import subprocess
import Cheetah.Template
_ = lambda x: x			# add fake gettext function until i fix up i18n

__all__ = ['manhelp', 'acquire_namespace']

class manhelp:

	def __init__(self, template, namespace={}):

		self.template = template
		self.namespace = namespace

		# process template
		self.groff = Cheetah.Template.Template(template, searchList=[namespace])


	def tostdout(self):
		"""write groff output to stdout."""
		try:
			f = sys.stdout
			f.write(str(self.groff))
			f.close()
			return True
		except IOError, e:
			return False


	def tofile(self, filename):
		"""write groff man page output to a file."""
		try:
			f = open(filename, 'w')
			f.write(str(self.groff))
			f.close()
			return True
		except IOError, e:
			return False


	def togzipfile(self, filename):
		"""write groff man page output to a gzip (.gz) file."""
		try:
			f = gzip.open(filename, 'wb')
			f.write(str(self.groff))
			f.close()
			return True
		except IOError, e:
			return False


def acquire_namespace(namespace, verbose=False):
	"""attempt to acquire namespace data that corresponds to the
	magic namespace identifier, e.g. {name:value} or module:func
	if no valid data can be found, then return an empty dict."""

	# attempt to get a function or value externally
	if type(namespace) is str:
		namespace = namespace.strip()	# cleanup
		# looks like we might have a literal dictionary to eval()
		if (namespace[0], namespace[-1]) == ('{', '}'):
			if verbose:
				print >> sys.stderr, _('trying to parse a dictionary...')
			try:
				namespace = eval(namespace)
			except SyntaxError, e:
				print >> sys.stderr, _('error: %s, while parsing:' % e)
				print >> sys.stderr, '%s' % namespace
				return {}	# set a default

		# maybe this is a module to open and look inside of...
		elif namespace.count(':') == 1:	# e.g. module:[func|var]
			if verbose:
				print >> sys.stderr, _('trying to parse a pointer...')
			name, attr = namespace.split(':')
			try:
				module = __import__(name, fromlist=name.split('.'))
				result = getattr(module, attr)
				# if this is a function, run it...
				if type(result) is type(lambda: True):
					try:
						namespace = result()
					except Exception, e:
						if verbose:
							print >> sys.stderr, _('function execution failed with: %s' % e)
						return {}
				# or maybe it's just an attribute
				else:
					namespace = result

			except ImportError, e:
				if verbose:
					print >> sys.stderr, _('error importing: %s.' % name)
				return {}

			except AttributeError, e:
				if verbose:
					print >> sys.stderr, _('missing attribute: %s.' % attr)
				return {}

		# string doesn't seem to have a sensible pattern
		else:
			if verbose:
				print >> sys.stderr, _('namespace didn’t match any signatures.')
			return {}

	# after all of the above, check if there's a dictionary
	if not type(namespace) is dict:
		if verbose:
			print >> sys.stderr, _('the `namespace\' option must evaluate to a dictionary.')
		return {}

	return namespace


def main(argv):
	"""main function for running manhelp as a script utility."""
	# run man with the output from the template
	if not os.name == 'posix':
		# TODO: maybe we could add something different for windows?
		print >> sys.stderr, 'sorry, your os cannot display man pages.'
		sys.exit(1)

	template = ''
	namespace = {}
	b = os.path.basename(argv[0])

	if len(argv) >= 3 and argv[1] in ['-m', '-x']:
		arg = argv.pop(1)
		if arg == '-m':
			# subprocess is pro magic. it's amazing that it works!
			# if you pay attention, the docs turn out to be great!
			# see: http://docs.python.org/library/subprocess.html
			p1 = subprocess.Popen(
				"./%s '%s' " % (b, "' '".join(argv[1:3])),
				shell=True, stdout=subprocess.PIPE
			)
			p2 = subprocess.Popen(
				["man --local-file -"],
				shell=True, stdin=p1.stdout
			)
			# wait for man to exit before continuing...
			sts = os.waitpid(p2.pid, 0)	# very important
			sys.exit()

	if len(argv) == 3:
		namespace = acquire_namespace(argv[2], verbose=True)

	if len(argv) in [2, 3]:
		template = argv[1]
		obj = manhelp(template, namespace)
		obj.tostdout()

	else:
		# usage and other cool tips
		print 'usage: ./%s template [namespace]' % b
		print 'extra: ./%s template [namespace] | man -l -' % b
		print 'extra: ./%s template [namespace] | gzip -f > gzoutput.gz' % b


if __name__ == '__main__':
	main(sys.argv)

