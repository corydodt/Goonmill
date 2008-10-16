# -*- coding: utf-8 -*-
## $Id: gather.py,v 1.1 2007/04/15 05:52:47 yosida Exp $
#
try :
    from _estraiernative import *
except ImportError :
    import sys; sys.path.insert(0, '../')
    from _estraiernative import *

# create the database object
db = Database()

# open the database
if not db.open("casket", Database.DBWRITER | Database.DBCREAT) :
    print "error: %s\n" % db.err_msg(db.error())
    raise SystemExit(1)    

# create a document object
doc = Document()

# add attributes to the document object
doc.add_attr("@uri", "http://estraier.gov/example.txt")
doc.add_attr("@title", "Over the Rainbow")

# add the body text to the document object
doc.add_text("Somewhere over the rainbow.  Way up high.")
doc.add_text("There's a land that I heard of once in a lullaby.")

# register the document object to the database
if not db.put_doc(doc, Database.PDCLEAN) :
    print "error: %s\n" % db.err_msg(db.error())
    raise SystemExit(1)
print "db.put_doc()"

# close the database
if not db.close() :
    print "error: %s\n" % db.err_msg(db.error())
    raise SystemExit(1)
print "db.close()"
