#
# Makefile for evanescent machine idle detection and shutdown tool.
# Copyright (C) 2008-2010  James Shubin, McGill University
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


# name of this project
NAME := $(shell basename `pwd`)

# version of the program
VERSION := $(shell cat VERSION)

# where am i ?
PWD := $(shell pwd)

# executables
RMTOOL = rm -i

# www source and metadata paths
WWW = $(PWD)/../www/code/$(NAME)/
METADATA = $(WWW)/$(NAME)
EXT = .tar.bz2

# TODO: it seems many use: '/usr' (less logical) and not '/usr/' (more logical)
PREFIX := $(shell ./findeva.py)


# if someone runs make without a target, print some useful messages
all:
	# list the available targets and what they do
	echo -e 'available targets:'
	echo -e '- clean:\tcleans up any files that can be generated again.'
	echo -e '- install:\tinstalls this package on the machine.'
	echo -e '- uninstall:\tuninstalls this package from the machine.'
	echo -e '- purge:\tdelete all traces of the install from the machine.'
	echo -e '- source:\tmake a source archive for distribution.'
	echo -e '- www:\t\tput an archive on the local webserver.'
	echo -e '- man:\t\tbuild the man pages and then view them.'


# clean up any mess that can be generated
clean: force
	# let distutils try to clean up first
	python setup.py clean
	# remove distutils mess with -f because they're write protected
	if [ -e build/ ]; then $(RMTOOL) -rf build/; fi
	# remove generated man mess
	$(RMTOOL) -r man/evanescent.* 2> /dev/null || true
	# remove any python mess (let above scripts rm the bulk first)
	find . -name '*.pyc' -type f -print0 | xargs -0 rm -f


# this installs code to your machine
install: clean
	python setup.py build
	sudo python setup.py install
	sudo mandb	# update the man index for `apropos' and `whatis'


# XXX: replace all of this with the distutils setup.py uninstall command i made
# uninstalls the package
uninstall:
	# FIXME: remove all the {site|dist}-packages of the right python version
	sudo $(RMTOOL) -r $(PREFIX)lib/python2.5/site-packages/evanescent/ 2> /dev/null || true
	sudo $(RMTOOL) -r $(PREFIX)share/evanescent/ 2> /dev/null || true
	sudo $(RMTOOL) $(PREFIX)bin/evanescent-daemon 2> /dev/null || true
	sudo $(RMTOOL) $(PREFIX)bin/evanescent-remote 2> /dev/null || true
	sudo $(RMTOOL) $(PREFIX)bin/evanescent-client 2> /dev/null || true
	sudo $(RMTOOL) $(PREFIX)lib/python2.5/site-packages/yamlhelp.py* 2> /dev/null || true
	sudo $(RMTOOL) $(PREFIX)lib/python2.5/site-packages/logginghelp.py* 2> /dev/null || true
	sudo $(RMTOOL) /etc/event.d/evanescent.upstart 2> /dev/null || true
	sudo $(RMTOOL) /etc/xdg/autostart/evanescent.desktop 2> /dev/null || true
	# TODO: i bet that dbus doesn't look in /usr/local/share/dbus-1/ ... should it ?
	sudo $(RMTOOL) /usr/share/dbus-1/services/ca.mcgill.cs.dazzle.evanescent.client.service 2> /dev/null || true
	sudo $(RMTOOL) $(PREFIX)share/man/man1/evanescent* 2> /dev/null || true
	sudo $(RMTOOL) -r $(PREFIX)share/doc/evanescent/ 2> /dev/null || true
	# egg files:
	sudo $(RMTOOL) $(PREFIX)lib/python2.5/site-packages/evanescent-* 2> /dev/null || true


# purge any unwanted files
purge: uninstall
	# these get created by evanescent, remove them on a purge
	# FIXME: these two should get the path from xdg
	$(RMTOOL) -r $(HOME)/.config/eva/ 2> /dev/null || true	# eva.conf.yaml
	$(RMTOOL) -r $(HOME)/.cache/eva/ 2> /dev/null || true	# eva.log
	sudo $(RMTOOL) /var/log/evanescent.log* 2> /dev/null || true
	sudo $(RMTOOL) /etc/evanescent.conf.yaml 2> /dev/null || true
	# empty man index even though this should eventually get updated by cron
	sudo mandb


# build the man pages, and then view them
man: force
	python setup.py build_manpages
	cd man/ ;\
	./viewthis.sh


# make a source package for distribution
source: clean
	# split this up into multiple lines for readability
	cd ..; \
	tar	--exclude=old \
		--exclude=play \
		--exclude=.swp \
		--exclude=.git \
		--exclude=.gitignore \
		--exclude=dist \
		--bzip2 \
		-cf $(NAME)$(EXT) $(NAME)/
	\
	if [ -e ./dist/$(NAME)-$(VERSION)$(EXT) ]; then \
		echo version $(VERSION) already exists; \
		rm ../$(NAME)$(EXT); \
	else \
		mv ../$(NAME)$(EXT) ./dist/$(NAME)-$(VERSION)$(EXT) && \
		echo 'source tarball created successfully in dist/'; \
	fi


www: force
	# rsync directories so they are equivalent in terms of files with: $EXT
	rsync -avz --include=*$(EXT) --exclude='*' --delete dist/ $(WWW)
	# empty the file
	echo -n '' > $(METADATA)
	cd $(WWW); \
	for i in *$(EXT); do \
		b=$$(basename $$i $(EXT)); \
		V=$$(echo -n $$(basename "`echo -n "$$b" | rev`" \
		"`echo -n "$(NAME)-" | rev`") | rev); \
		echo $(NAME) $$V $$i >> $(METADATA); \
	done; \
	sort -V -k 2 -o $(METADATA) $(METADATA)		# sort by version key


# depend on this fake target to cause a target to always run
force: ;


# this target silences echoing of any target which has it as a dependency.
.SILENT:

