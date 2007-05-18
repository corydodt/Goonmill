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
{
    python -c "$@" 2>&1
}

testPython "Install SQLAlchemy" < <(p 'import sqlalchemy')
testPython "Install zope.interface" < <(p 'import zope.interface')
t='from twisted import __version__ as v; assert v>="2.5.0", "Twisted ver. is %s" % (v,)'
testPython "Install Twisted 2.5" < <(p "$t")
testPython "Install Divmod Nevow" < <(p 'import nevow')
testPython "Install simpleparse" < <(p 'import simpleparse')
testPython "Python 2.5 is required for xml.etree" < <(p 'import xml.etree')

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
    echo ":: To restore it, type: gzip -dc $db > ${db/.gz/}"
    echo ":: Caution: This will DESTROY any changes you made to the database."
fi

echo "Done."