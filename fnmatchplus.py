#!/usr/bin/python
import re
import fnmatch

def fnmatchcaseplus(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This is a version of fnmatch() which doesn't case-normalize
    its arguments. It has been modified to return the match obj.
    """

    if not pat in fnmatch._cache:
        res = fnmatch.translate(pat)
        fnmatch._cache[pat] = re.compile(res)
    return fnmatch._cache[pat].match(name)

fnmatch.fnmatchcaseplus = fnmatchcaseplus


def fnsearchcaseplus(name, pat):
    """Test whether FILENAME is found in PATTERN, using search.

    This is a version of fnmatch() which does a search instead of
    a match in the pattern. It returns the search obj.
    """

    if not pat in fnmatch._cache:
        res = fnmatch.translate(pat)
        fnmatch._cache[pat] = re.compile(res)
    return fnmatch._cache[pat].search(name)

fnmatch.fnsearchcaseplus = fnsearchcaseplus

