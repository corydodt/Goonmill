"""Use: from goonmill._sparqlsandbox import *"""

import pprint

from rdflib import ConjunctiveGraph
import rdflib
from rdflib import RDFS
from rdflib.Namespace import Namespace as NS

from goonmill.rdfquery import fam, char, dice, pcclass, prop, db, prefixes

def getSandbox(select):
    print select
    pprint.pprint(
            list(
                db.query(select)
                )
            )

def reload():
    from goonmill import _sparqlsandbox
    import __builtin__
    getattr(__builtin__, 'reload')(_sparqlsandbox)

pprint.pprint(sorted(locals().keys()))
print "NAMESPACE PREFIXES: "
pprint.pprint(prefixes)
