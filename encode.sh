#!/bin/bash
#
#   Evanescent machine idle detection and shutdown tool.
#    Copyright (C) 2008  James Shubin, McGill University
#    Written for McGill University by James Shubin <purpleidea@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# this script encodes and stores a file as a special .py python file which can
# later be imported and decoded back into the original binary file.

# check usage
if [ "$1" == "" ]; then
	echo "usage: $0 <inputfile>"
	exit
fi

# replace all dots in the filename with underscores
# this is so that python doesn't choke on import
f=`echo -n "$1" | tr '.' '_'`

# add .py extension
f="$f.py"

# add a shebang to the file for fun
echo '#!/usr/bin/python' > "$f"

# store the original filename as a py variable
echo "filename = '$1'" >> "$f"

# begin the py heredoc variable
echo 'base64 = """' >> "$f"

# base64 encode the file
base64 $1 >> "$f"

# add the py heredoc terminators
echo '"""' >> "$f"

# echo the filename used
echo "$f"

