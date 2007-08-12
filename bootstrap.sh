#!/bin/bash
## Bootstrap setup for goonmill

cat <<EOF
:: This script will check your environment to make sure Goonmill is
:: ready to run, and do any one-time setup steps necessary.
::
:: Please check for any errors below, and fix them.
EOF

export errorStatus=""

function testPython()
# Use: testPython "Fix this thingie" <<<$(command)
#  If "command" has no output, we pass.
# 
#  If there is any output, the last line is considered an error message, and we
#  print it.  Then we set the global errorStatus.
# 
#  "command" should not write to stderr if possible, so use 2>&1 to redirect to
#  stdout.
{
    message="$1"
    # the last line read is the one we want
    while read l; do line="$l"; done

    if [ -n "$line" ]; then
        echo "** $message ($line)"
        errorStatus="error"
    else
        echo "OK"
    fi
}

function p()
# Run any python code and print its output or error to stdout.
{
    python -c "$@" 2>&1
}

testPython "Install SQLAlchemy" <<<$(p 'import sqlalchemy')
testPython "Install zope.interface" <<<$(p 'import zope.interface')
t="from twisted import __version__ as v
assert v>='2.5.0', 'Twisted ver. is %s' % (v,)"
testPython "Install Twisted 2.5" <<<$(p "$t")
testPython "Install Divmod Nevow" <<<$(p 'import nevow')
testPython "Install simpleparse" <<<$(p 'import simpleparse')
testPython "Install PyLucene" <<<$(p 'from PyLucene import *')

testPython "Install python-magic" <<<$(p 'import magic')
testPython "Python 2.5 is required for xml.etree" <<<$(p 'import xml.etree')

if [ "$errorStatus" == "error" ]; then
    echo "** Errors occurred.  Please fix the above errors, then re-run this script."
    exit 1
fi

db=goonmill/srd35.db.gz
if [ ! -r goonmill/srd35.db ]; then
    echo ":: Uncompressing database $db"
    gzip -dc $db > ${db/.gz/}
else
    echo "** ${db/.gz/} already exists, not willing to overwrite it!"
    echo ::
    echo :: If you have already run bootstrap.sh once, this is not an error.
    echo ::
    echo ":: To restore it, type: gzip -dc $db > ${db/.gz/}"
    echo :: Caution: This will DESTROY any changes you made to the database.
fi

echo "Done."
