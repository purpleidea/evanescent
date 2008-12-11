# in case someone runs make randomly
all:
	ls -lah

# clean up all the python mess
clean:
	rm -f *.pyc

# this target makes a package for distribution
tar: clean
	rm evanescent.tar.bz2 2> /dev/null || true
	cd .. && tar --exclude=old --exclude=play --exclude=evanescent.conf.yaml --bzip2 -cf evanescent.tar.bz2 evanescent/
	mv ../evanescent.tar.bz2 .
