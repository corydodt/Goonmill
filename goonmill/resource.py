"""
The resource structure for Goonmill

API for building the goonmill page and its fragments.
"""
import shlex

from zope.interface import implements

from nevow import rend, url, loaders, athena, static, page, vhost, inevow, tags as T

from nevow.testutil import renderLivePage, FragmentWrapper

from goonmill.util import RESOURCE, resourceData
from goonmill.history import History, Statblock

class Root(rend.Page):
    """
    Adds child nodes for things common to anonymous and logged-in root
    resources.
    """
    addSlash = True  # yeah, we really do need this, otherwise 404 on /
    def __init__(self, dev, *args, **kwargs):
        rend.Page.__init__(self, *args, **kwargs)
        self.dev = dev

        if self.dev:
            self.child_sandbox = self._child_sandbox
            self.child_dicebox = self._child_dicebox

    def _child_dicebox(self, ctx):
        from goonmill._dicesandbox import *
        return DiceSandboxPage()

    def _child_sandbox(self, ctx):
        from goonmill._sparqlsandbox import *
        return SandboxPage()

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
    docFactory = loaders.xmlfile(RESOURCE("templates/Search"))
    jsClass = u'Goonmill.Search'

    def __init__(self, *a, **kw):
        super(Search, self).__init__(*a, **kw)
        self.history = History()

    def setView(self, historyView):
        self.history.setView(historyView)
        self.historyView = historyView

    def onSearchSubmit(self, kwargs):
        # hidden import so twistd works when PyLucene isn't installed :(
        from goonmill import search
        # FIXME - shlex.split does something horribly broken here if you don't
        # call .encode on the unicode object
        terms = shlex.split(kwargs['search_terms'].encode('utf8'))
        hits = search.find(terms)
        return [(h.id, h.name, h.score) for h in hits]

    athena.expose(onSearchSubmit)

    def chose(self, id):
        """
        Respond to the action of a user choosing a hit from the search results
        """
        sb = Statblock.fromId(int(id))
        self.history.addStatblock(sb)
        return None

    athena.expose(chose)


class HistoryView(athena.LiveElement):
    """The results container widget"""
    docFactory = loaders.xmlfile(RESOURCE("templates/HistoryView"))
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
    docFactory = loaders.xmlfile(RESOURCE("templates/Result"))
    jsClass = u'Goonmill.Result'
    def __init__(self, statblock, *a, **kw):
        super(Result, self).__init__(*a, **kw)
        self.statblock = statblock
        self.guises = {}

    def slots(self, req, tag):
        s = self.statblock
        get = s.get

        def guise(label, readOnly=False, *a, **kw):
            if readOnly:
                _g = ReadOnlyGuise(*a, **kw)
            else:
                _g = Guise(*a, **kw)
            _g.setFragmentParent(self)
            self.guises[label] = _g
            return _g

        fill = tag.fillSlots

        # basic information block
        fill('count', guise('count',
            value=get('count'), 
            tooltip='Click to set the number of individuals', 
            template=resourceData('templates/Count'),
            editHandler=s.setCount))
        fill('label', guise('label', tooltip='Click to add a label', 
            editHandler=s.setLabel))
        fill('gender', '')
        fill('race', '')
        fill('class', '')
        fill('level', '')
        fill('name', get('name'))
        fill('challengeRating', get('challenge_rating'))
        fill('alignment', guise('alignment', 
            readOnly=False, value=get('alignment'), 
            tooltip='Click to edit alignment',
            editHandler=s.setAlignment))
        fill('size', get('size'))
        fill('creatureType', get('type'))
        fill('subtype', get('descriptor'))
        fill('initiative', get('initiative'))
        fill('senses', get('senses'))
        fill('listen', get('listen'))
        fill('spot', get('spot'))
        fill('aura', get('aura'))
        fill('languages', (get('languages'),))

        # defense block
        fill('ac', get('armor_class'))
        fill('specialAC', get('specialAC'))
        fill('acFeats', get('acFeats'))
        fill('hp', guise('hp', readOnly=True, value=get('hitPoints')))
        fill('hitDice', get('hitDice'))
        fill('fastHealing', get('fastHealing'))
        fill('regeneration', get('regeneration'))
        fill('damageReduction', get('damageReduction'))
        fill('immunities', get('immunities'))
        fill('resistances', get('resistances'))
        fill('spellResistance', get('spellResistance'))
        fill('fort', get('fort'))
        fill('ref', get('ref'))
        fill('will', get('will'))
        ## vulnerabilities - see renderer

        # attack block
        fill('speed', get('speed'))
        fill('speedFeats', get('speedFeats'))
        ## meleeAttacks - see renderer
        ## rangedAttacks - see renderer
        fill('rangedAttackFeats', get('rangedAttackFeats'))
        fill('space', get('space'))
        fill('reach', get('reach'))
        fill('baseAttack', get('base_attack'))
        fill('grapple', get('grapple'))
        fill('attackOptionFeats', get('attackOptionFeats'))
        fill('attackOptions', get('special_attacks') or '-')
        fill('specialActions', get('specialActions'))
        ## gear TODO
        fill('casterLevel', get('casterLevel'))
        fill('spells', guise('spells', 
            readOnly=False, value='',
            tooltip='Click to edit spells',
            editHandler=s.setSpells))
        ## spellLikeAbilities - see renderer

        # skills, abilities, feats block
        fill('abilities', get('abilities'))
        fill('specialQualities', get('special_qualities'))
        fill('feats', get('feats') or '-')
        fill('skills', get('skills'))
        ## possessions TODO
        fill('spellbook', guise('spellbook', 
            readOnly=False, value='',
            tooltip='Click to edit spellbook',
            editHandler=s.setSpellbook))

        # ability detail drilldown block
        ## fullAbilities - see renderer

        s.updateHandler(self.updateHandler)

        return tag

    page.renderer(slots)

    def updateHandler(self, attribute, newValue):
        self.guises[attribute].push(newValue)

    def immunities(self, req, tag):
        if self.statblock.get('immunities'):
            return tag
        return ''

    page.renderer(immunities)

    def spells(self, req, tag):
        if self.statblock.get('casterLevel'):
            return tag
        return ''

    page.renderer(spells)

    def specialAC(self, req, tag):
        if self.statblock.get('specialAC'):
            return tag
        return ''

    page.renderer(specialAC)

    def specialActions(self, req, tag):
        if self.statblock.get('specialActions'):
            return tag
        return ''

    page.renderer(specialActions)

    def resistances(self, req, tag):
        if self.statblock.get('resistances'):
            return tag
        return ''

    page.renderer(resistances)

    def spellResistance(self, req, tag):
        if self.statblock.get('spellResistance'):
            return tag
        return ''

    page.renderer(spellResistance)

    def fastHealing(self, req, tag):
        if self.statblock.get('fastHealing'):
            return tag
        return ''

    page.renderer(fastHealing)

    def damageReduction(self, req, tag):
        if self.statblock.get('damageReduction'):
            return tag
        return ''

    page.renderer(damageReduction)

    def regeneration(self, req, tag):
        if self.statblock.get('regeneration'):
            return tag
        return ''

    page.renderer(regeneration)

    def aura(self, req, tag):
        if self.statblock.get('aura'):
            return tag
        return ''

    page.renderer(aura)

    def subtype(self, req, tag):
        if self.statblock.get('descriptor'):
            return tag
        return ''

    page.renderer(subtype)

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

    def acFeats(self, req, tag):
        feats = self.statblock.acFeats()
        if len(feats) > 0:
            return tag

        return ''

    page.renderer(acFeats)

    def speedFeats(self, req, tag):
        feats = self.statblock.speedFeats()
        if len(feats) > 0:
            return tag

        return ''

    page.renderer(speedFeats)

    def vulnerabilities(self, req, tag):
        vulns = self.statblock.get('vulnerabilities')
        if not vulns:
            return ''

        content = []
        pg = tag.patternGenerator('vulnerability')
        for n, vuln in enumerate(vulns):
            if n < len(vulns) - 1:
                vuln = vuln + ', '
            content.append(pg().fillSlots('attackEffect', vuln))

        return tag[content]

    page.renderer(vulnerabilities)

    def meleeAttacks(self, req, tag):
        groups = self.statblock.get('attackGroups')['melee']
        content = []
        pg = tag.patternGenerator('meleeAttack')
        for group in groups:
            content.append(pg().fillSlots('value', group))

        return tag[content]

    page.renderer(meleeAttacks)

    def rangedAttacks(self, req, tag):
        groups = self.statblock.get('attackGroups')['ranged']
        content = []
        pg = tag.patternGenerator('rangedAttack')
        for group in groups:
            content.append(pg().fillSlots('value', group.capitalize()))

        return tag[content]

    page.renderer(rangedAttacks)

    def attackOptionFeats(self, req, tag):
        feats = self.statblock.attackOptionFeats()
        if len(feats) > 0:
            return tag

        return ''

    page.renderer(attackOptionFeats)

    def rangedAttackFeats(self, req, tag):
        feats = self.statblock.rangedAttackFeats()
        if len(feats) > 0:
            return tag

        return ''

    page.renderer(rangedAttackFeats)

    def spellLikeAbilities(self, req, tag):
        spellLikes = self.statblock.get('spellLikeAbilities')
        if spellLikes:
            return tag[[T.xml(s) for s in spellLikes]]

        return ''

    page.renderer(spellLikeAbilities)

    def fullAbilities(self, req, tag):
        fulls = self.statblock.get('fullAbilities')
        if fulls:
            return tag[[T.xml(f) for f in fulls]]

        return ''

    page.renderer(fullAbilities)


class Guise(athena.LiveElement):
    """
    A simple edit/static toggleable widget.  It can also receive a push from
    the server.

    @param value: The default value of the widget
    @param tooltip: The tooltip that will appear when the user hovers over the
                    widget
    @param editHandler: A callable that takes the new value as an argument
                        when the user edits a Guise in the browser
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/Guise'))
    jsClass = u"Goonmill.Guise"

    def __init__(self, value='', tooltip='Click to edit', editHandler=None,
            template=None,
            *a, **kw):
        super(Guise, self).__init__(*a, **kw)
        self.value = value
        self.tooltipText = tooltip
        self.editHandler = editHandler
        self.template = template

    def preload(self, req, tag):
        return self.value

    page.renderer(preload)

    def tooltip(self, req, tag):
        return self.tooltipText

    page.renderer(tooltip)

    def editedValue(self, newValue):
        """User edited the value in the browser"""
        self.editHandler(newValue)

    athena.expose(editedValue)

    def push(self, newValue):
        """
        Send a value to the widget to be displayed.
        """
        return self.callRemote('pushed', unicode(newValue))

    def getInitialArguments(self):
        return (self.template,)


class ReadOnlyGuise(Guise):
    docFactory = loaders.xmlfile(RESOURCE('templates/ReadOnlyGuise'))
    jsClass = u'Goonmill.ReadOnlyGuise'


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


class StyledFragmentWrapper(FragmentWrapper):
    docFactory = loaders.xmlstr("""<html xmlns:n="http://nevow.com/ns/nevow/0.1">
<head><link rel="stylesheet" type="text/css" href="../static/goonmill.css" />
<meta name="content-type" http-equiv="text/html; charset=utf-8" />
</head>
<body n:render="fragment" />
</html>""")
    # fold nicely.


if __name__ == '__main__': # {{{
    # render each and every monster
    from goonmill import query2
    ids = query2._allIds()
    
    docFactory = loaders.stan(
                    T.html[
                        T.body[
                            T.directive('fragment')]])
    for id in ids:
        print id,

        sb = Statblock.fromId(id)
        result = Result(sb)
        wrapper = StyledFragmentWrapper(result)

        def _gotResult(r):
            file(RESOURCE('html/%s.html' % (id,)), 'w').write(r)

        renderLivePage(wrapper).addCallback(_gotResult)
# }}}
