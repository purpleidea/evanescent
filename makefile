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

# version and revision of the program
VERSION := $(shell cat VERSION)


# if someone runs make randomly
all:
	ls -lah


# clean up any mess that can be generated
clean: force

	# let distutils try to clean up first
	python setup.py clean

	# remove any python mess
	rm -f *.pyc

	# remove the python windowless mess too
	rm -f *.pyw

	# remove the tar archive
	rm evanescent.tar.bz2 2> /dev/null || true

	# remove distutils mess
	rm -r build/ 2> /dev/null || true
	rm -r dist/ 2> /dev/null || true


install:
	# this runs distutils for the install
	sudo python setup.py install


uninstall:

	# remove what distutils installs
	rm -r /usr/lib/python2.5/site-packages/evanescent/ 2> /dev/null || true
	rm -r /usr/share/evanescent/ 2> /dev/null || true
	rm /usr/bin/evanescent-daemon.py 2> /dev/null || true
	rm /usr/bin/evanescent-remote.py 2> /dev/null || true
	rm /usr/bin/evanescent-client.py 2> /dev/null || true
	rm /usr/lib/python2.5/site-packages/yamlhelp.py 2> /dev/null || true
	rm /usr/lib/python2.5/site-packages/yamlhelp.pyc 2> /dev/null || true
	rm /usr/lib/python2.5/site-packages/logginghelp.py 2> /dev/null || true
	rm /usr/lib/python2.5/site-packages/logginghelp.pyc 2> /dev/null || true
	rm /etc/event.d/evanescent.upstart 2> /dev/null || true
	rm /etc/xdg/autostart/evanescent.desktop 2> /dev/null || true
	rm /usr/share/dbus-1/services/ca.mcgill.cs.dazzle.evanescent.client.service 2> /dev/null || true
	rm /etc/evanescent.conf.yaml.example 2> /dev/null || true
	# egg files:
	rm /usr/lib/python2.5/site-packages/evanescent-* 2> /dev/null || true


purge: uninstall
	# these get created by evanescent, remove them on a purge
	rm $(HOME)/.eva.conf.yaml 2> /dev/null || true
	rm $(HOME)/.eva.log 2> /dev/null || true
	rm /var/log/evanescent.log 2> /dev/null || true
	rm /etc/evanescent.conf.yaml 2> /dev/null || true


# make a package for distribution
tar: clean

	cd .. && tar --exclude=old --exclude=play --exclude=.swp --exclude=.bzr --exclude=tar --exclude=packages --bzip2 -cf evanescent.tar.bz2 evanescent/
	mv ../evanescent.tar.bz2 ./tar/evanescent-$(VERSION).tar.bz2


# make a package for windows...
windows:
	# the client needs a windowless version
	#cp eva.py eva.pyw
	echo 'figure out py2exe and do it...'


# this target does nothing, and can be used as a dependency when we always want
# to run the commands, irregardless of whatever make thinks needs to run.
force: ;


# how do i fix this so that the pwd's are the same and you get persistence in makefiles?
TODO:
	pwd
	cd windows
	pwd


TODO2:
	pwd; cd windows; pwd


# unix2dos file ending conversion
# perl -pe 's/\r\n|\n|\r/\r\n/g' inputfile > outputfile


