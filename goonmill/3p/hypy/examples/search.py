# -*- coding: utf-8 -*-
## $Id: search.py,v 1.1 2007/04/15 05:52:47 yosida Exp $
#
try :
    from _estraiernative import *
except ImportError :
    import sys; sys.path.insert(0, '../')
    from _estraiernative import *

# create the database object
db = Database()

# open the database
if not db.open("casket", Database.DBREADER) :
    print "error: %s\n", db.err_msg(db.error)
    raise SystemExit(1)

# create a search condition object
cond = Condition()

# set the search phrase to the search condition object
cond.set_phrase("rainbow AND lullaby")

# get the result of search
result = db.search(cond)

# for each document in the result
dnum = result.doc_num()
for i in range(0, dnum) :
    # retrieve the document object
    doc = db.get_doc(result.get_doc_id(i), 0)
    if doc is None :
        continue
        
    # display attributes
    uri = doc.attr("@uri")
    if uri :
        print "URI: %s", uri
    title = doc.attr("@title")
    if title :
        print "Title: %s", title

    # display the body text
    for text in doc.texts() :
        print "%s", text

# close the database
if not db.close() :
    print "error: %s", db.err_msg(db.error)

