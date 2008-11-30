
========
Goonmill
========

Goonmill is a D&D-focused web application which generates quick statblocks
for SRD monsters.

It will allow you to quickly create a bunch of printable statblocks suitable
for your next D&D session.



============
Architecture
============

...


============
Installation
============

(Ubuntu instructions.  Linux is required to run Goonmill as far as I know.
Other distributions of Linux will work fine, but you'll have to figure it out
from the output of bootstrap.sh.)

1. Run bootstrap.sh (in the same directory as this README.txt) and it will
tell you which dependencies you are currently deficient on.  If you know what
you're doing, you can just install them and don't bother to refer to the rest
of this file.  bootstrap.sh is kept up-to-date better than this file is, and
should reliably tell you when something you need is missing.

2. Install Playtools.
sudo apt-get install python python-pysqlite2 
sudo easy_install rdflib storm http://playtools-source.goonmill.org/archive/tip.tar.gz

3. Install the rest of Goonmill's dependencies
sudo apt-get install python-twisted python-nevow python-simpleparse \
    python-zopeinterface hyperestraier libestraier8-dev libqdbm14-dev

4. Build estraiernative, the Python bindings for the search library.
cd goonmill/3p/estraiernative-cdd
sudo python setup.py install

5. Run bootstrap.sh one more time.  This time it will generate all the runtime
files Goonmill needs to launch.

# 6. TODO - images


========
Starting
========

To start a server for debugging, run ./cycle in the root directory and visit
    http://localhost:6680/app/ws/0.12345/

