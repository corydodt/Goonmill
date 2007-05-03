#!/bin/bash
## Bootstrap setup for goonmill

cat <<EOF
:: This script will check your environment to make sure Goonmill is
:: ready to run, and do any one-time setup steps necessary.
::
:: Please check for any errors below, and fix them.
EOF

function testPython()
{
    message="$1"
    # the last line read is the one we want
    while read l; do line="$l"; done

    if [ -n "$line" ]; then
        echo "$message ($line)"
    else
        echo "OK"
    fi
}

function p()
{
    python -c "$@" 2>&1
}

p 'import sqlalchemy' | testPython "Install SQLAlchemy"
p 'import zope.interface' | testPython "Install zope.interface"
p 'from twisted import __version__ as v; assert v>="2.5.0", "Twisted version is %s" % (v,)' | testPython "Install Twisted 2.5"
p 'import nevow' | testPython "Install Divmod Nevow"
p 'import simpleparse' | testPython "Install simpleparse"
p 'import xml.etree' | testPython "Python 2.5 is required for xml.etree"


echo ":: Uncompressing database"
gzip -dc goonmill/srd35.db.gz > goonmill/srd35.db

echo "Done."
