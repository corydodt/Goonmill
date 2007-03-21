"""The resource structure for Goonmill"""
import shlex

from nevow import rend, url, loaders, athena, flat, static

from goonmill.util import RESOURCE
from goonmill.history import History, Statblock
from goonmill import query

class Root(rend.Page):
    """
    Adds child nodes for things common to anonymous and logged-in root
    resources.
    """
    addSlash = True  # yeah, we really do need this, otherwise 404 on /
    def child_static(self, ctx):
        return static.File(RESOURCE('static'))

    def child_app(self, ctx):
        return GoonmillPage()

    def renderHTTP(self, ctx):
        return url.root.child("app")

class GoonmillPage(athena.LivePage):
    docFactory = loaders.xmlfile(RESOURCE('templates/goonmillpage.xhtml'))
    addSlash = 1
    
    def render_all(self, ctx, data):
        s = Search()
        s.setFragmentParent(self)

        hv = HistoryView()
        hv.setFragmentParent(self)

        s.setView(hv)

        return [s, hv]

class Search(athena.LiveElement):
    """The search widget"""
    docFactory = loaders.xmlfile(RESOURCE("elements/Search"))
    jsClass = u'Goonmill.Search'

    def __init__(self, *a, **kw):
        super(Search, self).__init__(*a, **kw)
        self.history = History()

    def setView(self, historyView):
        self.history.setView(historyView)
        self.historyView = historyView

    def onSearchSubmit(self, kwargs):
        # FIXME - shlex.split does something horribly broken here if you don't
        # call .encode on the unicode object
        terms = shlex.split(kwargs['search_terms'].encode('utf8'))
        hits = query.find(terms)
        return [(h.id, h.name) for h in hits]

    athena.expose(onSearchSubmit)

    def onConfigSubmit(self, kwargs):
        """Take the configured monster and make a statblock for it"""
        id = kwargs['monster_id']
        label = kwargs['monster_label']
        count = kwargs['monster_count']
        ## TODO - create a statblock for this monster
        sb = Statblock(id, count, label)
        self.historyView.addStatblock(sb)

    athena.expose(onConfigSubmit)

    def chose(self, id):
        """
        Respond to the action of a user choosing a hit from the search results
        """
        ## TODO figure out special configure parameters we could play with
        ## frex - parse organization to suggest a value for count
        ##      - parse attack to present options for weapon choices
        goon = query.lookup(id)
        return self.callRemote('setupConfigure', id, goon.name)

    athena.expose(chose)

class HistoryView(athena.LiveElement):
    """The results container widget"""
    docFactory = loaders.xmlfile(RESOURCE("elements/HistoryView"))
    jsClass = u'Goonmill.HistoryView'

    ## def forgetStatblock(self, statblock):
    ##    TODO - remove a statblock from the seen list in response
    ##    to a user clicking the 'delete' button next to it,
    ##    and tell the browser we did this

    def historyUpdated(self, history):
        outgoing = []
        for statblock in history.pendingStatblocks():
            outgoing.append(Result(statblock))

        d = self.callRemote("postResult", outgoing)

        def unpend(r):
            """
            On successful post, notify history that statblocks are no
            longer "pending"
            """
            history.unpendStatblocks(outgoing)
            return r

        d.addCallback(unpend)

        return d

class Result(athena.LiveElement):
    """One result"""
    docFactory = loaders.xmlfile(RESOURCE("elements/Result"))
    def __init__(self, statblock, *a, **kw):
        super(Result, self).__init__(*a, **kw)
        self.statblock = statblock

    def render_name(self, ctx, data):
        return "ID: %s " % (self.statblock.id,)

