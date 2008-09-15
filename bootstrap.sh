#!/bin/bash
## Bootstrap setup for goonmill

umask 002

cat <<EOF
:: This script will check your environment to make sure Goonmill is
:: ready to run, and do any one-time setup steps necessary.
::
:: Please check for any errors below, and fix them.
EOF

export errorStatus=""

function testPython()
# Use: testPython "Software name" "python code"
#  If "python code" has no output, we pass.
# 
#  If there is any output, the last line is considered an error message, and
#  we print it.  Then we set the global errorStatus.
# 
#  "python code" should not write to stderr if possible, so use 2>&1 to
#  redirect to stdout.
{
    software="$1"
    line=$(python -c "$2" 2>&1 | tail -1)

    if [ -n "$line" ]; then
        echo "** Install $software ($line)"
        errorStatus="error"
    else
        echo "OK $software"
    fi
}

testPython "Playtools" 'import playtools'
testPython "RDFlib" 'import rdflib'
testPython "Storm" 'import storm.locals'
testPython "zope.interface" 'import zope.interface'
t="from twisted import __version__ as v; assert v>='2.5.0', 'Have %s' % (v,)"
testPython "Twisted 2.5" "$t"
testPython "Divmod Nevow" 'import nevow'
testPython "simpleparse" 'import simpleparse'
testPython "PyLucene" 'from lucene import *'
testPython "Python 2.5" 'import xml.etree'

if [ "$errorStatus" == "error" ]; then
    echo "** Errors occurred.  Please fix the above errors, then re-run this script."
    exit 1
fi

echo "Done."

config=goonmill/tripledb.n3
if [ ! -r "$config" ]; then
    cp -v "$config".sample "$config" || exit 1
else
    echo "** ${config} already exists, not willing to overwrite it!"
    echo ::
    echo :: If you have already run bootstrap.sh once, this is not an error.
    echo ::
fi

userdb=goonmill/user.db
if [ ! -r "$userdb" ]; then
    sqlite3 -init goonmill/sql/user.sql $userdb '.exit' || exit 1
    sqlite3 -init goonmill/sql/dummy.sql $userdb '.exit' || exit 1
    chmod 664 $userdb
else
    echo "** ${userdb} already exists, not willing to overwrite it!"
    echo ::
    echo :: If you have already run bootstrap.sh once, this is not an error.
    echo ::
fi

