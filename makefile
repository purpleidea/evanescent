#
#    Makefile for evanescent machine idle detection and shutdown tool.
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

# in case someone runs make randomly
all:
	ls -lah


clean: force
	# remove any python mess
	rm -f *.pyc

	# remove the tar archive
	rm evanescent.tar.bz2 2> /dev/null || true

	# remove the files in clean
	for f in `cat clean`; do rm $$f; done

	# remove the `clean' file
	rm clean 2> /dev/null || true


revno:
	# make a version file
	echo -n 'VERSION ' > VERSION

	# use the bzr numbering for unique identification of packages
	bzr revno >> VERSION


# make a package for distribution
tar: clean revno encode

	cd .. && tar --exclude=old --exclude=play --exclude=.bzr --bzip2 -cf evanescent.tar.bz2 evanescent/
	mv ../evanescent.tar.bz2 .


# make a package for windows...
windows: encode
	echo 'figure out py2exe and do it...'


encode:
	# empty the clean file
	echo -n '' > clean
	# find out which files need encoding and loop through them
	# then encode each one, saving the outputted filename
	# next, move that file to the main directory
	# then save each generated filename in a `clean' file for later deletion
	cd 'windows/' ; for x in `./../encoded.py`; do y=`./../encode.sh "$$x"`; mv $$y '../' ; echo `basename $$y` >> ../clean; done


# this target does nothing, and can be used as a dependency when we always want
# to run the commands, irregardless of whatever make thinks needs to run.
force: ;


# how do i fix this so that the pwd's aren't the same and you get persistence in makefiles?
FIXME:
	pwd
	cd windows
	pwd

FIXME2:
	pwd; cd windows; pwd

# unix2dos file ending conversion
# perl -pe 's/\r\n|\n|\r/\r\n/g' inputfile > outputfile


