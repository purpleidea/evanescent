# in case someone runs make randomly
all:
	ls -lah

# clean up all the python mess
clean:
	rm -f *.pyc

revno:
	echo -n 'VERSION ' > VERSION
	bzr revno >> VERSION

# this target makes a package for distribution
tar: clean revno
	rm evanescent.tar.bz2 2> /dev/null || true
	cd .. && tar --exclude=old --exclude=play --exclude=evanescent.conf.yaml --exclude=.bzr --bzip2 -cf evanescent.tar.bz2 evanescent/
	mv ../evanescent.tar.bz2 .

# make a package for windows...
windows:
	echo 'figure out py2exe and do it...'

# unix2dos file ending conversion
# perl -pe 's/\r\n|\n|\r/\r\n/g' inputfile > outputfile
	

