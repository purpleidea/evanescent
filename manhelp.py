#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Manhelp wrapper to simplify creation of man pages.
    Copyright (C) 2009  James Shubin, McGill University
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

# NOTE: a useful guide to actually writing man pages can be found at:
# http://www.schweikhardt.net/man_page_howto.html

# TODO: manhelp could be extended to aid in actually generating nroff, e.g.:
# http://andialbrecht.wordpress.com/2009/03/17/creating-a-man-page-with-distutils-and-optparse/

import os
import sys
import gzip
import subprocess
import Cheetah.Template
import Cheetah.NameMapper
_ = lambda x: x			# add fake gettext function until i fix up i18n

__all__ = ['manhelp', 'acquire_namespace']

class manhelp:

	def __init__(self, template, namespace={}):

		self.template = template
		self.namespace = namespace

		# process template
		if os.path.isfile(self.template):
			self.groff = Cheetah.Template.Template(file=template, searchList=[namespace])
		else:
			self.groff = Cheetah.Template.Template(template, searchList=[namespace])
		try:
			self.groff = str(self.groff)	# runs the NameMapper
		except Cheetah.NameMapper.NotFound, e:
			print >> sys.stderr, _('namespace error: %s' % e)
			self.groff = ''


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
	# NOTE: if you run this program as: `./manhelp.py -m', you get -m to
	# stdout. this is because it assumes -m is the template. NOT a bug.
	def usage():
		"""print usage information."""
		# usage and other cool tips
		print _('usage: ./%s template [namespace] (nroff to stdout)' % b)
		print _('extra: ./%s -m template [namespace] (nroff to man)' % b)
		print _('extra: ./%s -z template [namespace] (write gz man)' % b)
		#print _('extra: ./%s template [namespace] | gzip -f > gzoutput.gz' % b)

	if not os.name == 'posix':
		# TODO: maybe we could add something for windows?
		print >> sys.stderr, _('sorry, your os cannot display man pages.')
		sys.exit(1)

	template = ''
	namespace = {}
	b = os.path.basename(argv[0])

	# TODO: in the future, when manhelp generates nroff, we should add a gz
	# option that takes the man section number and writes out the name.#.gz
	# filename into the current directory. it makes sense to wait for nroff
	# generation so that we can get the name and section number dynamically
	if len(argv) >= 3 and argv[1] in ['-m', '-z']:
		arg = argv.pop(1)
		if arg == '-m':
			# subprocess is pro magic. it's amazing that it works!
			# if you pay attention, the docs turn out to be great!
			# see: http://docs.python.org/library/subprocess.html
			p1 = subprocess.Popen(['python', b] + argv[1:3], stdout=subprocess.PIPE)
			p2 = subprocess.Popen(['man', '--local-file', '-'], stdin=p1.stdout)
			sts = os.waitpid(p2.pid, 0)	# important to wait!
		elif arg == '-z':
			raise NotImplementedError('auto generating gzip man pages is yet to come!')

		sys.exit()

	if len(argv) == 3:
		namespace = acquire_namespace(argv[2], verbose=True)

	if len(argv) in [2, 3]:
		template = argv[1]
		obj = manhelp(template, namespace)
		obj.tostdout()
	else:
		usage()


if __name__ == '__main__':
	main(sys.argv)

