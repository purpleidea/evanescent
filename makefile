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
# TODO: don't hardcode what we don't need to. eg: the '/usr' prefix, etc...
# maybe we can get prefix from my ./configure shell script ?

# if someone runs make without a target, print some useful messages
all:
	# list the available targets and what they do
	echo -e 'available targets:'
	echo -e '- clean:\tcleans up any mess or files that can be generated again.'
	echo -e '- install:\tinstalls evanescent on the machine.'
	echo -e '- uninstall:\tuninstalls evanescent from the machine.'
	echo -e '- purge:\tremoves all traces of evanescent from a machine.'
	echo -e '- commit:\truns some pre-commit housekeeping scripts.'
	echo -e '- tar:\t\tmake a tar.bz2 archive for distribution.'
	echo -e '- www:\t\tput an archive on the local webserver.'
	echo -e '- man:\t\tbuild the man pages and then view them.'


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


# this should be run before an important commit
# it takes care of running version.sh, etc...
commit: clean force
	./version.sh
	echo "you now probably want to run:"
	echo "$ bzr commit -m '<comment>'"
	echo "$ make tar"
	echo "$ make www"


# this runs distutils for the install
install: clean
	python setup.py build
	sudo python setup.py install


# remove all the mess that distutils installed
uninstall:
	sudo rm -r /usr/lib/python2.5/site-packages/evanescent/ 2> /dev/null || true
	sudo rm -r /usr/share/evanescent/ 2> /dev/null || true
	sudo rm /usr/bin/evanescent-daemon 2> /dev/null || true
	sudo rm /usr/bin/evanescent-remote 2> /dev/null || true
	sudo rm /usr/bin/evanescent-client 2> /dev/null || true
	sudo rm /usr/lib/python2.5/site-packages/yamlhelp.py* 2> /dev/null || true
	sudo rm /usr/lib/python2.5/site-packages/logginghelp.py* 2> /dev/null || true
	sudo rm /etc/event.d/evanescent.upstart 2> /dev/null || true
	sudo rm /etc/xdg/autostart/evanescent.desktop 2> /dev/null || true
	sudo rm /usr/share/dbus-1/services/ca.mcgill.cs.dazzle.evanescent.client.service 2> /dev/null || true
	sudo rm /usr/share/man/man1/evanescent.1.gz 2> /dev/null || true
	sudo rm -r /usr/share/doc/evanescent/ 2> /dev/null || true
	# egg files:
	sudo rm /usr/lib/python2.5/site-packages/evanescent-* 2> /dev/null || true


# purge all extra unwanted files
purge: uninstall
	# these get created by evanescent, remove them on a purge
	# FIXME: these two should get the path from xdg
	rm -rf $(HOME)/.config/eva/ 2> /dev/null || true	# eva.conf.yaml
	rm -rf $(HOME)/.cache/eva/ 2> /dev/null || true		# eva.log
	sudo rm /var/log/evanescent.log 2> /dev/null || true
	sudo rm /etc/evanescent.conf.yaml 2> /dev/null || true


# build the man pages, and then view them
man: force
	python setup.py build_manpages
	cd man/ ;\
	./viewthis.sh


# make a package for distribution
tar: clean

	# split this up into multiple lines for readability
	cd ..; \
	tar	--exclude=old \
		--exclude=play \
		--exclude=.swp \
		--exclude=.bzr \
		--exclude=tar \
		--bzip2 \
		-cf evanescent.tar.bz2 evanescent/

	if [ -e ./tar/evanescent-$(VERSION).tar.bz2 ]; then \
		echo version $(VERSION) already exists; \
		rm ../evanescent.tar.bz2; \
	else \
		mv ../evanescent.tar.bz2 ./tar/evanescent-$(VERSION).tar.bz2; \
	fi


# move current version to www folder
www: .SILENT

	if [ -e /var/www/code/evanescent-$(VERSION).tar.bz2 ]; then \
		echo version $(VERSION) already exists in /var/www/; \
	else \
		if [ -e ./tar/evanescent-$(VERSION).tar.bz2 ]; then \
			cp -a ./tar/evanescent-$(VERSION).tar.bz2 /var/www/code/; \
			echo EVANESCENT $(VERSION) evanescent-$(VERSION).tar.bz2 >> /var/www/code/evanescent; \
			echo version $(VERSION) successfully pushed to local webserver; \
			echo you might want to sync public webserver with local; \
		else \
			echo version $(VERSION) doesn\'t exist as a tarball; \
		fi \
	fi


# make a package for windows...
windows:
	# the client needs a windowless version
	#cp eva.py eva.pyw
	echo 'figure out py2exe and do it...'


# this target does nothing, and can be used as a dependency when we always want
# to run the commands, irregardless of whatever make thinks needs to run.
force: ;


# this target silences echoing of any target which has it as a dependency.
.SILENT:


# NOTE: this is how you would get instance persistence in makefile lines:
example: force
	pwd; \
	cd play; \
	pwd

