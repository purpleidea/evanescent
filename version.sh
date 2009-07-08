#!/bin/bash

# AGPLv.3
# james shubin <purpleidea@gmail.com>
# simple script to make the VERSION file intelligently

function usage() {
	echo "usage: $0 <VERSION> [ <FILENAME> ]"
	echo "writes version info in <FILENAME> using major version: <VERSION>"
	echo "<FILENAME> defaults to: \`VERSION' if not specified."
	exit 1
}

# check usage
if ([ ! $# -eq 1 ] && [ ! $# -eq 2 ]) ||
[ "$1" == "-h" ] || [ "$1" == "--help" ]; then
	usage
fi

# default filename
FILENAME="VERSION"

# override the default
if [ "$2" != "" ]; then
	FILENAME=$2
fi

# get the revision number somehow
REVNO=`bzr revno`

# add 1 so that newly committed versioned VERSION file matches the new revision
PLUS1=`echo $REVNO+1 | bc`

# build string
VERSION="$1-$PLUS1"

# write string to file
echo $VERSION > $FILENAME

# print status message
echo "\`$VERSION' stored in $FILENAME"

