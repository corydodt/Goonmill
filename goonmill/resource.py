"""The resource structure for Goonmill"""
import shlex

from nevow import rend, url, loaders, athena, flat, static, page

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
        count = int(kwargs['monster_count'])

        # limit the count to something reasonable to prevent DoS
        if count > 100: count = 100

        sb = Statblock(id, count, label)
        self.history.addStatblock(sb)

    athena.expose(onConfigSubmit)

    def chose(self, id):
        """
        Respond to the action of a user choosing a hit from the search results
        """
        ## TODO figure out special configure parameters we could play with
        ## frex - parse attack to present options for weapon choices
        ##      - parse alignment to suggest values for alignment
        ##      - suggest gender?
        goon = query.lookup(id)
        return self.callRemote('setupConfigure', id, goon.name, goon.organization)

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
        pending = history.pendingStatblocks()
        for statblock in pending:
            r = Result(statblock)
            r.setFragmentParent(self)
            outgoing.append(r)

        d = self.callRemote("postResult", outgoing)

        # immediately un-pend statblocks we have posted.
        # there's no point keeping them around if they failed to post
        history.unpendStatblocks(pending)

        return d

class Result(athena.LiveElement):
    """One result"""
    docFactory = loaders.xmlfile(RESOURCE("elements/Result"))
    def __init__(self, statblock, *a, **kw):
        super(Result, self).__init__(*a, **kw)
        self.statblock = statblock
        self.monster = statblock.monster
        self.label = statblock.label
        self.hitPoints = statblock.hitPoints

    def slots(self, req, tag):
        m = self.monster
        tag.fillSlots('name', m.name)
        tag.fillSlots('challengeRating', m.challenge_rating)
        tag.fillSlots('alignment', m.alignment)
        tag.fillSlots('size', m.size)
        tag.fillSlots('creatureType', m.type)
        tag.fillSlots('initiative', m.initiative)
        tag.fillSlots('languages', u'LANGUAGES=FIXME')
        return tag

    page.renderer(slots)

    def blockLabel(self, req, tag):
        if self.label:
            tag.fillSlots('label', self.label)
            return tag
        return ''

    page.renderer(blockLabel)

    def subtype(self, req, tag):
        if self.monster.descriptor:
            tag.fillSlots('subtype', self.monster.descriptor)
            return tag
        return ''

    page.renderer(subtype)

    def aura(self, req, tag):
        return u"FIXME - aura"

    page.renderer(aura)

    def space(self, req, tag):
        m = self.monster
        # don't need to print anything if this is just a typical Medium
        # monster
        if m.space == u'5 ft.' and m.reach == u'5 ft.' and m.size == u'Medium':
            return ''

        tag.fillSlots('space', m.space)
        tag.fillSlots('reach', m.reach)
        return tag

    page.renderer(space)

    def npcTraits(self, req, tag):
        return "FIXME - npcTraits"
        """
        GENDER
        RACE
        CLASS
        LEVEL
        """

    page.renderer(npcTraits)

    def hp(self, req, tag):
        tag.fillSlots('hp', ', '.join(map(unicode, self.hitPoints)))
        return tag

    page.renderer(hp)
