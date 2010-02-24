#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Evanescent machine idle detection and shutdown tool manual namespace.

This file provides useful namespace info to be used with the cheetah template.
"""
# Copyright (C) 2008-2009  James Shubin, McGill University
# Written for McGill University by James Shubin <purpleidea@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import datetime
import misc
from jhelp import manhelp

__all__ = ['namespace']

# namespace to be used by manhelp module for man page formatting
namespace = {
	'name': 'evanescent',
	'version': misc.get_version(),
	'authors': (misc.get_authors(split=True), misc.get_authors(split=False)),
	'date': datetime.datetime.fromtimestamp(os.path.getmtime('VERSION')),
}
# install special namespace of manhelp formatters into the namespace we'll use.
manhelp.install(namespace)

