# hypy version of the estraiernative gather example

from hypy import HDatabase, HCondition

# open the database, read-only
db = HDatabase()
db.open('casket', 'r')

# create a search condition object
cond = HCondition(u'lull*')

# get the result of search
result = db.search(cond)

# iterate the result
for doc in result:
    # display attributes
    print 'URI: %s' % (doc[u'@uri'].encode('utf-8'),)
    print "Title: %s" % (doc[u'@title'].encode('utf-8'),)

    # display the body text
    for t in doc.getTexts():
        print t.encode('utf-8')

# close the database
db.close()
