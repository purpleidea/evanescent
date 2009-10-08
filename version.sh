#!/bin/bash

# AGPLv.3
# James Shubin <purpleidea@gmail.com>
# simple script to make the VERSION file intelligently

function usage() {
	echo "usage: $0 <VERSION> [ <FILENAME> ]"
	echo "writes version info in <FILENAME> using major version: <VERSION>"
	echo "<FILENAME> defaults to: \`VERSION' if not specified."
	exit 1
}

# check usage
if [ $# -eq 0 ]; then
	# prompt for a version
	read -p 'version series: ' NEWVERSION
elif ([ ! $# -eq 1 ] && [ ! $# -eq 2 ]) ||
[ "$1" == "-h" ] || [ "$1" == "--help" ]; then
	usage
fi

# default filename
FILENAME="VERSION"

# default version
if [ "$1" != "" ]; then
	NEWVERSION=$1
fi

# override the default
if [ "$2" != "" ]; then
	FILENAME=$2
fi

# get the revision number somehow
REVNO=`bzr revno`

# add 1 so that newly committed versioned VERSION file matches the new revision
PLUS1=`echo $REVNO+1 | bc`

# build string
VERSION="$NEWVERSION-$PLUS1"

# write string to file
echo $VERSION > $FILENAME

# print status message
echo "\`$VERSION' stored in $FILENAME"

