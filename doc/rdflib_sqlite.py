"""
Demonstrating how to instantiate and use a sqlite-based triplestore
"""

import rdflib
from rdflib.Graph import ConjunctiveGraph as Graph
from rdflib import plugin
from rdflib.store import Store, VALID_STORE
from rdflib import Namespace
from rdflib import Literal
from rdflib import URIRef

from pysqlite2.dbapi2 import OperationalError

default_graph_uri = "http://rdflib.net/rdfstore"
configString = "/home/cdodt/wc/Goonmill/goonmill"

# Get the sqlite plugin. You may have to install the python sqlite libraries
store = plugin.get('SQLite', Store)('rdfstore.db')

# Open previously created store, or create it if it doesn't exist yet
try:
    rt = store.open(configString,create=False)
except OperationalError, e:
    try:
        # There is no underlying sqlite infrastructure, create it
        rt = store.open(configString,create=True)
        assert rt == VALID_STORE
    except OperationalError, e:
        raise
        import sys, pdb; pdb.post_mortem(sys.exc_info()[2])
 
# There is a store, use it
graph = Graph(store, identifier = URIRef(default_graph_uri))

print "Triples in graph before add: ", len(graph)

# Now we'll add some triples to the graph & commit the changes
rdflibNS = Namespace('http://rdflib.net/test/')
graph.add((rdflibNS['pic:1'], rdflibNS['name'], Literal('Jane & Bob')))
graph.add((rdflibNS['pic:2'], rdflibNS['name'], Literal('Squirrel in Tree')))
graph.commit()

print "Triples in graph after add: ", len(graph)

# display the graph in RDF/XML
print graph.serialize()
