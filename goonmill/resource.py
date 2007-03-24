"""The resource structure for Goonmill"""
import shlex

from zope.interface import implements, Interface

from nevow import rend, url, loaders, athena, flat, static, page, vhost, inevow

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

        return ctx.tag[s, hv]


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

    def chose(self, id):
        """
        Respond to the action of a user choosing a hit from the search results
        """
        sb = Statblock(id)
        self.history.addStatblock(sb)
        return None

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

    def slots(self, req, tag):
        get = self.statblock.get

        def guise(*a, **kw):
            _g = Guise(*a, **kw)
            _g.setFragmentParent(self)
            return _g

        fill = tag.fillSlots
        fill('name', get('name'))
        fill('label', guise(tooltip='Click to add a label'))
        fill('challengeRating', get('challenge_rating'))
        fill('alignment', guise(get('alignment'), 'Click to edit alignment'))
        fill('size', get('size'))
        fill('creatureType', get('type'))
        fill('initiative', get('initiative'))
        fill('languages', u'LANGUAGES=FIXME')
        fill('speed', get('speed'))
        fill('baseAttack', get('base_attack'))
        fill('abilities', get('abilities'))
        fill('specialQualities', get('special_qualities'))
        fill('subtype', get('descriptor'))
        fill('count', guise(get('count'), 
                    tooltip='Click to set the number of individuals'))
        fill('space', get('space'))
        fill('reach', get('reach'))
        fill('gender', '')
        fill('race', '')
        fill('class', '')
        fill('level', '')
        return tag

    page.renderer(slots)

    def subtype(self, req, tag):
        if self.statblock.get('descriptor'):
            return tag
        return ''

    page.renderer(subtype)

    def count(self, req, tag):
        if self.statblock.get('count') > 1:
            return tag
        return ''

    page.renderer(count)

    def aura(self, req, tag):
        return tag[u"FIXME - aura"]

    page.renderer(aura)

    def space(self, req, tag):
        g = self.statblock.get
        # don't need to print anything if this is just a typical Medium
        # monster
        space = g('space')
        reach = g('reach')
        if space == u'5 ft.' and reach == u'5 ft.' and g('size') == u'Medium':
            return ''

        return tag

    page.renderer(space)

    def npcTraits(self, req, tag):
        return tag["FIXME - npcTraits"]

    page.renderer(npcTraits)

    def hp(self, req, tag):
        tag.fillSlots('hp', ', '.join(map(str, self.statblock.hitPoints())))
        return tag

    page.renderer(hp)


class Guise(athena.LiveElement):
    """A simple edit/static toggleable widget
    @param value: The default value of the widget
    @param tooltip: The tooltip that will appear when the user hovers over the widget
    @param edit: A string that names a handler defined in Result object
    """
    docFactory = loaders.xmlfile(RESOURCE('elements/Guise'))
    jsClass = u"Goonmill.Guise"

    def __init__(self, value='', tooltip='Click to edit', *a, **kw):
        super(Guise, self).__init__(*a, **kw)
        self.value = value
        self.tooltipText = tooltip

    def preload(self, req, tag):
        return self.value

    page.renderer(preload)

    def tooltip(self, req, tag):
        return self.tooltipText

    page.renderer(tooltip)


class VhostFakeRoot:
    """
    I am a wrapper to be used at site root when you want to combine 
    vhost.VHostMonsterResource with nevow.guard. If you are using guard, you 
    will pass me a guard.SessionWrapper resource.
    """
    implements(inevow.IResource)
    def __init__(self, wrapped):
        self.wrapped = wrapped
    
    def renderHTTP(self, ctx):
        return self.wrapped.renderHTTP(ctx)
        
    def locateChild(self, ctx, segments):
        """Returns a VHostMonster if the first segment is "vhost". Otherwise
        delegates to the wrapped resource."""
        if segments[0] == "VHOST":
            return vhost.VHostMonsterResource(), segments[1:]
        else:
            return self.wrapped.locateChild(ctx, segments)
