#!/usr/bin/python
# -*- coding: utf-8 -*-
"""distutils.command.build_manpages

Implements the Distutils 'build_manpages' command.
"""

# created 2009/10/05, James Shubin

__revision__ = "$Id$"		# TODO: what should i do with this?

import os.path			# for os.path.isfile()
import distutils.core		# from distutils.core import Command
import distutils.command.build	# from distutils.command.build import build
import distutils.errors		# from distutils.errors import DistutilsOptionError
import manhelp			# to generate man pages
_ = lambda x: x			# add fake gettext function until i fix up i18n

class build_manpages(distutils.core.Command):
	# FIXME: use the dry-run option...
	description = "generates nroff man pages from templates"
	user_options = [
		('gzoutput=', 'o', "specifies the gzip output file location"),
		('template=', 't', "specifies which man page template file"),
		('namespace=', 'n', "specifies the manhelp namespace function"),
	]


	def initialize_options(self):
		self.gzoutput = None
		self.template = None
		self.namespace = {}


	def finalize_options(self):
		# do some validation
		if type(self.gzoutput) is not str:
			raise distutils.errors.DistutilsOptionError(
			_('the `gzoutput\' option is required.')
			)

		if not(type(self.template) is str) or \
		not(os.path.isfile(self.template)):
			raise distutils.errors.DistutilsOptionError(
			_('the `template\' option requires an existing file.')
			)

		# process self.namespace
		self.namespace = manhelp.acquire_namespace(self.namespace, \
							verbose=self.verbose)


	def run(self):
		if self.verbose: print 'namespace is: %s' % self.namespace
		if self.verbose: print 'template file is: %s' % self.template
		if self.verbose: print 'gzoutput file is: %s' % self.gzoutput

		obj = manhelp.manhelp(self.template, self.namespace)
		obj.togzipfile(self.gzoutput)


# add this command as a dependency to the build command
# TODO: add a predicate that checks if the man page has been recently built
# FROM: http://docs.python.org/distutils/apiref.html#distutils.cmd.Command
# The parent of a family of commands defines sub_commands as a class attribute;
# it’s a list of 2-tuples (command_name, predicate), with command_name a string
# and predicate an unbound method, a string or None. predicate is a method of
# the parent command that determines whether the corresponding command is
# applicable in the current situation. (Eg. we install_headers is only
# applicable if we have any C header files to install.) If predicate is None,
# that command is always applicable.
distutils.command.build.build.sub_commands.append(('build_manpages', None))

