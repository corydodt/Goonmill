# hypy version of the estraiernative gather example

from hypy import HDatabase, HDocument

# open the database
db = HDatabase()
db.open('casket', 'w')

# create a document object
doc = HDocument(uri=u'http://estraier.gov/example.txt')
doc[u'@title'] = u'Over the Rainbow'

# add the body text to the document object
doc.addText(u"Somewhere over the rainbow.  Way up high.")
doc.addText(u"There's a land that I heard of once in a lullaby.")

# register the document object to the database
db.putDoc(doc, clean=True)
print "db.putDoc()"

# close the database
db.close()
print "db.close()"
