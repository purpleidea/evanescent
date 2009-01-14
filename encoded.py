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

# enter a list of file names here that need to be encoded
files = ['p_GetLastInput.dll', 'widle.bat', 'widle.vbs']

# what nlines are these supposed to use?
nline = [False, '\r\n', '\r\n']

# make the filename `fixed' version so python doesn't choke
encoded = [ f.replace('.', '_') for f in files ]

# join them with spaces so we can loop through when called from our makefile
if __name__ == '__main__':
	print ' '.join(files)
