"""
SPARQL-y

A really stupid SPARQL query string builder
"""

from string import Template

from rdflib import ConjunctiveGraph
import rdflib

class SelectQuery(object):
    """
    I represent a SELECT query that can be turned into a query string.  I will
    hold things like base and default namespaces.

    >>> s = SPARQLQuery("http://thesoftworld.com/2007/family.n3")
    """
    def __init__(self, base, rest):
        self.base = base
        self.rest = rest
        self.namespaces = {}

    def stringifyPrefixes(self):
        return "\n".join([
            "PREFIX %s: <%s>" % (pfx, namespace) for
            (pfx, namespace) in self.namespaces.items()
            ])

    def __str__(self):
        d = dict(base=self.base, rest=self.rest, prefixes=self.stringifyPrefixes())
        return """BASE <%(base)s>
%(prefixes)s
%(rest)s
""" % d
        ""

    def bind(self, prefix, namespace):
        """Make this prefix refer to this namespace for this query."""
        self.namespaces[prefix] = namespace


def select(base, prefixes, rest):
    qry = SelectQuery(base, rest)
    for pfx, namespace in prefixes.items():
        qry.bind(pfx, namespace)
    return str(qry)


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
        assert len(data) == 1
        return data[0]

    def retrieveData(self, db, key):
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
        self.prefixes = prefixes
        [self.graph.load(d, format='n3') for d in datasets]

    def query(self, rest):
        sel = select(self.base, self.prefixes, rest)
        ## print sel
        ret = self.graph.query(sel)
        return ret

    def formatDatasetsClause(self):
        ret = []
        for ds in self.datasets:
            ret.append("FROM <%s>" % (ds,))

        return '\n'.join(ret)



def iriToTitle(iri):
    """Return the fragment id of the iri, in title-case"""
    uri = iri.lstrip('<').rstrip('>')
    return uri.split('#')[1].title()
