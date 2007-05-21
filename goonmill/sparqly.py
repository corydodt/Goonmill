"""
SPARQL-y

A really stupid SPARQL query string builder
"""

from string import Template

from rdflib import ConjunctiveGraph
import rdflib
from rdflib import RDFS


def select(base, rest):
    d = dict(base=base, rest=rest, )
    return """BASE <%(base)s> %(rest)s""" % d


def iriToTitle(iri):
    """Return the fragment id of the iri, in title-case"""
    uri = iri.lstrip('<').rstrip('>')
    return uri.split('#')[1].title()


NODEFAULT = ()

class SparqAttribute(object):
    """One attribute on a SparqItem, denoting type
    """
    def __init__(self, selector, default=NODEFAULT):
        self.selector = Template(selector)
        self.default = default

    def solve(self, db, key):
        """Return the value or values for this query."""
        data = self.retrieveData(db, key)
        if len(data) == 0:
            return None
        assert len(data) == 1
        return data[0]

    def retrieveData(self, db, key):
        # rdflib.URIRef could be passed as key; handle that case
        if hasattr(key, 'n3'):
            key = key.n3()

        rest = self.selector.safe_substitute(key=key)
        data = [r[0] for r in db.query(rest)]  ## TODO - support multiple variable queries? probably not
        if len(data) == 0:
            if self.default is NODEFAULT:
                return None

            if isinstance(self.default, SparqAttribute):
                return self.default.solve(db, key)

            return self.default
        return data


class URI(SparqAttribute):
    """An attribute that returns as an rdflib.URIRef"""


class Literal(SparqAttribute):
    """An attribute that returns as a rdflib.Literal"""


class Ref(SparqAttribute):
    """
    An item that must be loaded via another SparqItem
    """
    def __init__(self, itemClass, selector):
        self.itemClass = itemClass
        self.selector = selector
        super(Ref, self).__init__(selector)

    def solve(self, db, key):
        data = self.retrieveData(db, key)

        ret = []
        cls = self.itemClass

        if data is None:
            return ret

        for i in data:
            assert isinstance(i, rdflib.URIRef), (
                    "This query returned literals, not URIs!\n-- %s" % (i,))
            # pull the uri string from each data item
            att = cls(db=db, key=i.n3())
            ret.append(att)

        return ret


class Key(SparqAttribute):
    def __init__(self, transform=None):
        self.transform = transform
        super(Key, self).__init__('')

    def solve(self, db, key):
        if self.transform:
            key = self.transform(key)
        return [key]


class SparqItem(object):
    """An item composed of SPARQL queries against the store.
    Built out of SparqAttributes like this:

    class Thinger(SparqItem):
        slangName = Literal("SELECT ?slang $datasets { $key :slangName ?slang }")

    >>> myThinger = Thinger(db=someTripleStore, key=':marijuana')
    >>> myThinger.myAttr
    "Wacky Tabacky"
        
    """
    label = Literal(
        'SELECT ?l { $key rdfs:label ?l }', default=Key(transform=iriToTitle))
    comment = Literal('SELECT ?d { $key rdfs:comment ?d }', default='')

    def __init__(self, db, key):
        self.db = db
        self.key = key

    def __getattribute__(self, k):
        real = super(SparqItem, self).__getattribute__(k)
        if isinstance(real, SparqAttribute):
            return real.solve(db=self.db, key=self.key)
        return real


class TriplesDatabase(object):
    """A database from the defined triples"""
    def __init__(self, base, prefixes, datasets):
        self.graph = ConjunctiveGraph()
        self.base = base
        self.prefixes = {'rdfs': RDFS.RDFSNS}
        self.prefixes.update(prefixes)
        [self.graph.load(d, format='n3') for d in datasets]

    def query(self, rest):
        sel = select(self.base, rest)
        ## print sel
        ret = self.graph.query(sel, initNs=self.prefixes)
        return ret

    def formatDatasetsClause(self):
        ret = []
        for ds in self.datasets:
            ret.append("FROM <%s>" % (ds,))

        return '\n'.join(ret)


