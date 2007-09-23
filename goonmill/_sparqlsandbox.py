"""Use: from goonmill._sparqlsandbox import *"""

import pprint

from rdflib import ConjunctiveGraph
import rdflib
from rdflib import RDFS
from rdflib.Namespace import Namespace as NS

from nevow import athena, loaders, tags as T, flat

from goonmill.rdfquery import (fam, char, dice, pcclass, prop, db,
        Family, Sense, Language, CombatMechanic, SpecialAbility,
        SpecialQuality, Resistance)
from goonmill.util import RESOURCE

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
pprint.pprint(db.prefixes)


class SandboxPage(athena.LivePage):
    # FIXME - for now, just use the goonmill page
    docFactory = loaders.xmlfile(RESOURCE('templates/goonmillpage.xhtml'))
    addSlash = 1
    
    def render_all(self, ctx, data):
        s = SparqlSandbox()
        s.setFragmentParent(self)

        return ctx.tag[s, ]


class SparqlSandbox(athena.LiveElement):
    """A playground for running SPARQL queries."""
    docFactory = loaders.xmlfile(RESOURCE("elements/SparqlSandbox"))
    jsClass = u'Goonmill.SparqlSandbox'

    def setView(self, historyView):
        self.history.setView(historyView)
        self.historyView = historyView

    def showPrefixes(self, req, tag):
        t = T.table(_class="prefixes")
        for pfx, iri in db.prefixes.items():
            t[T.tr[T.td[repr(pfx), ':'], T.td['<', str(iri), '>']]]

        return tag[t]

    athena.renderer(showPrefixes)

    def onQuerySubmit(self, query):
        rows = []
        try:
            res = list(db.query(query))
        except SyntaxError, e: # ugh, why couldn't they define their own?
            err = T.span(_class="error")[str(e)]
            return unicode(flat.flatten(err))

        for n, row in enumerate(res):
            if n%2 == 0:
                rowStyle = 'even'
            else:
                rowStyle = 'odd'
            rows.append(T.tr(_class=rowStyle)[ [T.td[c] for c in row] ])

        table = flat.flatten([T.table[rows]])
        return unicode(table)

    athena.expose(onQuerySubmit)


