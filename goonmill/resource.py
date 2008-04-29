"""
The resource structure for Goonmill

API for building the goonmill page and its fragments.
"""
import random

from zope.interface import Interface, implements

from nevow import rend, url, loaders, athena, static, guard, page

from twisted.cred.portal import Portal
from twisted.cred.credentials import IAnonymous
from twisted.cred.checkers import AllowAnonymousAccess

from .util import RESOURCE
from .user import (Groupie, Workspace, Constituent, KIND_MONSTERGROUP, KIND_NPC,
            KIND_STENCIL, KIND_ENCOUNTER)
from . import search

TOO_MANY_GROUPIES = 123


class Root(rend.Page):
    """
    Adds child nodes for things common to anonymous and logged-in root
    resources.
    """
    addSlash = True  # yeah, we really do need this, otherwise 404 on /
    realm = None
    checkers = None
    _wrapper = None

    def child_static(self, ctx):
        return static.File(RESOURCE('static'))

    def child_app(self, ctx):
        if self._wrapper is None:
            self._wrapper = guardedWrapper(self.realm, self.checkers)
        return self._wrapper

    def renderHTTP(self, ctx):
        return url.root.child("app")


class GuardedRoot(rend.Page):
    """
    The /app part of webspace
    """
    addSlash = True

    def __init__(self, user, userDatabase, *a, **kw):
        self.user = user
        self.userDatabase = userDatabase
        rend.Page.__init__(self, *a, **kw)

    def renderHTTP(self, ctx):
        """Redirect to a new empty workspace"""
        x = random.random()
        u = url.URL.fromString('/app/ws/%s' % (x,))
        return u

    def locateChild(self, ctx, segs):
        if segs[0] == 'ws':
            # look up workspace. if it belongs to a user, make sure it belongs
            # to me.
            key = unicode(segs[1])
            ws = self.userDatabase.find(Workspace, Workspace.url ==
                    key).one()

            if self.user is None:
                if not ws:
                    ws = Workspace()
                    ws.url = key
                    self.userDatabase.add(ws)
                    self.userDatabase.commit()
                page = WorkspacePage(ws, None)
                return (page, segs[2:])

            else:
                if ws in self.user.workspaces:
                    page = WorkspacePage(ws, self.user)
                    return (page, segs[2:])

            return (None, ())

        return rend.Page.locateChild(self, ctx, segs)


def guardedWrapper(realm, checkers):
    ptl = Portal(realm)
    ptl.registerChecker(AllowAnonymousAccess(), IAnonymous)
    for checker in checkers:
        ptl.registerChecker(checker)
    # FIXME - this should be another wrapper, which returns a SessionWrapper,
    # which has persistentCookies set or not.  for now, all cookies are
    # persistent for a week
    wrap = guard.SessionWrapper(ptl)
    wrap.persistentCookies = True
    wrap.sessionLifetime = 3600 * 24 * 7
    return wrap


class WorkspacePage(athena.LivePage):
    """
    The entire workspace area, where the user spends most of his time
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/workspace.xhtml'))
    addSlash = 1

    def __init__(self, workspace, user, *a, **kw):
        self.workspace = workspace
        self.user = user
        athena.LivePage.__init__(self, *a, **kw)

    def render_workspace(self, ctx, data):
        eb = EventBus()
        eb.setFragmentParent(self)
        ctx.tag.fillSlots('eventBus', eb)
        self.eventBus = eb

        title = WorkspaceTitle(self.workspace)
        title.setFragmentParent(self)
        ctx.tag.fillSlots('titleEdit', title)

        cl = ConstituentList(self.workspace)
        cl.setFragmentParent(self)
        ctx.tag.fillSlots('constituentList', cl)

        self.constituentList = cl

        bs = BasicSearch(self.workspace)
        bs.setFragmentParent(self)
        ctx.tag.fillSlots('basicSearch', bs)

        mainActions = MainActions()
        mainActions.setFragmentParent(self)
        ctx.tag.fillSlots('mainActions', mainActions)

        wnt = WhichNewThing()
        ctx.tag.fillSlots('whichNewThing', wnt)

        return ctx.tag


class IWarmControl(Interface):
    """
    A WarmControl can be set from the server or the client.
    """
    def setLocally(value):
        """
        Set value, then return the old value
        """

    def serverUpdate(value):
        """
        Server code wants to change the value.  Change first, then notify
        client of change.
        """

    def clientUpdated(value):
        """
        Client code has changed the value.  Validate, then set here, or report
        an error to the client.
        """

    def rollback(reason, oldValue, newValue):
        """
        Called when serverUpdate fails at the client end.  oldValue and
        newValue are the value the server had before anything was done, and
        the value that was attempted to be set, respectively.  reason is
        the exception (failure instance), which would most usefully contain
        the fallback value the client attempted to make the field, assuming it
        could not use newValue for some reason.  i.e. truncating the field and
        returning ClientApproximationError("Foo bar baz ...")
        """

    def validate(value):
        """
        Verify that the value is useful
        """

    def init():
        """
        Initial renderer
        """


class InvalidValueError(Exception):
    pass


class WarmControl(athena.LiveElement):
    """
    A control which can be configured to be set from either the server or the
    client, with validation and rollback on BOTH sides
    """
    implements(IWarmControl)

    def init(self):
        raise NotImplemented("Implement init in a subclass")

    def rollback(self, reason, oldValue, newValue):
        raise NotImplemented("Implement rollback in a subclass")

    def setLocally(self, value):
        raise NotImplemented("Implement setLocally in a subclass")

    def validate(self, value):
        return True

    def serverUpdate(self, value):
        if not self.validate(value):
            raise InvalidValueError(value)

        original = self.setLocally(value)

        d = self.callRemote('serverUpdated', value)
        d.addErrback(lambda failure: self.rollback(failure, original, value))

        return d

    @athena.expose
    def clientUpdated(self, value):
        if not self.validate(value):
            raise InvalidValueError(value)

        original = self.setLocally(value)

        return value
 

class WarmText(WarmControl):
    """
    A text edit control
    """
    jsClass = u'Goonmill.WarmText'
    defaultText = u'Click to edit'

    def validate(self, value):
        """
        Simplest DOS-prevention.. limit length.  Adjust if necessary in
        subclasses.
        """
        return len(value) < 2000

    def getInitialArguments(self):
        return (self.defaultText, )


class WorkspaceTitle(WarmText):
    """
    The title of the workspace, at the top
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/WorkspaceTitle'))

    def __init__(self, workspace, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.workspace = workspace

    @page.renderer
    def init(self, req, tag):
        ws = self.workspace
        if ws.name is None:
            self.setLocally(u'Unnamed Workspace')
        tag.fillSlots('value', ws.name)
        return tag

    def rollback(self, failure, oldValue, newValue):
        self.workspace.name = oldValue
        from .user import theStore
        theStore.commit()

    def setLocally(self, value):
        original = self.workspace.name
        self.workspace.name = value
        from .user import theStore
        theStore.commit()
        return original


class ConstituentList(athena.LiveElement):
    """
    The workspace's list of constituent monsters in the center-left panel
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/ConstituentList'))
    jsClass = u'Goonmill.ConstituentList'

    def __init__(self, workspace, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.workspace = workspace

    @page.renderer
    def init(self, req, tag):
        pg = tag.patternGenerator('constituent')
        for c in self.workspace.constituents:
            pat = pg()

            pat.fillSlots('constituentKind', 'kind-%s' % (c.kind,))

            if c.isLibraryKind():
                pat.fillSlots('closingXTitle', 
                        'Remove from this workspace')
            else:
                pat.fillSlots('closingXTitle', 'Delete')

            base = c.getStencilBase()
            if base and c.kind == KIND_MONSTERGROUP:
                pat.fillSlots('constituentName', base.name)
            else:
                pat.fillSlots('constituentName', c.name)

            pat.fillSlots('constituentDetail', c.briefDetail())
            pat.fillSlots('constituentId', c.id)

            tag[pat]
        return tag

    @athena.expose
    def displayConstituent(self, id):
        from .user import theStore
        c = theStore.get(Constituent, id)

        if c.kind == KIND_NPC:
            view = NPCView(c)
        elif c.kind == KIND_MONSTERGROUP:
            view = MonsterGroupView(c)
        else:
            raise NotImplemented('other kinds')

        view.setFragmentParent(self.fragmentParent.eventBus)

        return view

    @athena.expose
    def removeConstituent(self, id):
        from .user import theStore
        constituent = theStore.get(Constituent, id)
        assert constituent in self.workspace.constituents

        if constituent.isLibraryKind(): 
            constituent.workspaceId = None
        else:
            theStore.remove(constituent)
        theStore.commit()
        return u'removed'

    def addMonsterGroup(self, constituent):
        """
        Tell the client to render a monster group in this list
        """
        name = constituent.getStencilBase().name
        detail = constituent.briefDetail()

        return self.callRemote("addConstituent", 
                constituent.kind, constituent.id, name, detail)

    def addNPC(self, constituent):
        """
        Tell the client to render an npc in this list
        """
        name = constituent.getStencilBase().name
        detail = constituent.briefDetail()

        return self.callRemote("addConstituent", 
                constituent.kind, constituent.id, name, detail)


class MainActions(athena.LiveElement):
    """
    The links in the top-left bar that create new things.
    """
    jsClass = u'Goonmill.MainActions'
    docFactory = loaders.xmlfile(RESOURCE('templates/MainActions'))
    

class BasicSearch(athena.LiveElement):
    """
    Search widget in the lower-left corner
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/BasicSearch'))
    jsClass = u"Goonmill.BasicSearch"

    def __init__(self, workspace):
        self.workspace = workspace
        athena.LiveElement.__init__(self)

    @athena.expose
    def searched(self, searchTerms):
        terms = searchTerms.split()
        self.lastFound = search.find(terms)
        return [(t.name, int(t.id), int(t.score * 100)) for t in self.lastFound]

    @athena.expose
    def newMonsterGroup(self, stencilId, count):
        from .query2 import db
        m = db.lookup(stencilId)
        c = Constituent.monsterGroupKind(m, count, self.workspace)
        mgv = MonsterGroupView(c)
        mgv.setFragmentParent(self.fragmentParent.eventBus)

        d = self.fragmentParent.constituentList.addMonsterGroup(c)

        def _monsterGroupWasListed(_):
            return mgv

        d.addCallback(_monsterGroupWasListed)
        return d

    @athena.expose
    def newNPC(self, stencilId):
        from .query2 import db
        m = db.lookup(stencilId)
        c = Constituent.npcKind(m, self.workspace)

        npcv = NPCView(c)
        npcv.setFragmentParent(self.fragmentParent.eventBus)

        d = self.fragmentParent.constituentList.addNPC(c)

        def _npcWasListed(_):
            return npcv

        d.addCallback(_npcWasListed)
        return d


class EventBus(athena.LiveElement):
    """
    An event handler.  This simply fires events on the document element, which
    other widgets can listen for.
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/EventBus'))
    jsClass = u'Goonmill.EventBus'

    # TODO - drop this class entirely.  this is completely implemented in
    # javascript now.


class WhichNewThing(page.Element):
    """
    A dialog box to ask whether you want a new NPC or Monster Group
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/WhichNewThing'))


class MonsterGroupView(athena.LiveElement):
    """
    The view of a monster group in the main page
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/MonsterGroup'))
    jsClass = u"Goonmill.MonsterGroup"

    def __init__(self, constituent):
        self.constituent = constituent
        athena.LiveElement.__init__(self)

    @page.renderer
    def initialize(self, req, tag):
        name = self.constituent.getStencilBase().name
        tag.fillSlots('monsterName', name)

        mgroup = self.constituent.fuckComponentArchitecture()
        gn = GroupName(mgroup)
        gn.setFragmentParent(self)
        tag.fillSlots('groupName', gn)

        return tag

    @page.renderer
    def monsterGroupList(self, req, tag):
        mg = self.constituent.fuckComponentArchitecture()
        pg = tag.patternGenerator("monsterGroupRow")
        for groupie in mg.groupies:
            groupie.randomize(overwrite=False)

            gn = GroupieName(groupie)
            gn.setFragmentParent(self)

            ghp = GroupieHitPoints(groupie)
            ghp.setFragmentParent(self)

            gg = GroupieGear(groupie)
            gg.setFragmentParent(self)

            gs = GroupieSpells(groupie)
            gs.setFragmentParent(self)

            ga = GroupieAlignment(groupie)
            ga.setFragmentParent(self)

            pat = pg()
            pat.fillSlots('hitPoints', ghp)
            pat.fillSlots('alignment', ga)
            pat.fillSlots('gear', gg)
            pat.fillSlots('spells', gs)
            pat.fillSlots('personalName', gn)
            pat.fillSlots('groupieId', groupie.id)
            tag[pat]
        return tag

    @athena.expose
    def increaseGroupies(self, amount):
        """
        Add 'amount' more groupies.

        Returns a new widget to display by cloning me.
        """
        cn = self.constituent
        mg = cn.fuckComponentArchitecture()
        total = len(list(mg.groupies)) + amount
        assert total <= TOO_MANY_GROUPIES


        from .user import theStore
        for n in range(amount):
            groupie = Groupie()
            groupie.monsterGroup = mg
            groupie.randomize()
            theStore.add(groupie)
        theStore.commit()

        newMg = MonsterGroupView(self.constituent)
        newMg.setFragmentParent(self.fragmentParent)
        self.detach()
        return newMg

    @athena.expose
    def deleteChecked(self, ids):
        """
        Remove from the group the groupies identified by 'ids'

        Returns count of removed.
        """
        from .user import theStore
        for id in ids:
            groupie = theStore.get(Groupie, id)
            theStore.remove(groupie)
        theStore.commit()

        return len(ids)

    def getInitialArguments(self):
        return [self.constituent.id]

    @athena.expose
    def randomizeChecked(self, ids):
        """
        Randomize groupies identified by 'ids'

        Returns a new monstergroup widget to display
        """
        cn = self.constituent
        mg = cn.fuckComponentArchitecture()

        from .user import theStore
        for id in ids:
            groupie = theStore.get(Groupie, id)
            groupie.randomize(overwrite=True)
        theStore.commit()

        newMg = MonsterGroupView(self.constituent)
        newMg.setFragmentParent(self.fragmentParent)
        self.detach()
        return newMg


class GroupieHitPoints(WarmText):
    """
    Change the hit points on a groupie
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/GroupieHitPoints'))
    def __init__(self, groupie, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.groupie = groupie 

    @page.renderer
    def init(self, req, tag):
        hp = self.groupie.hitPoints
        assert hp is not None
        tag.fillSlots('value', hp)
        return tag

    def rollback(self, failure, oldValue, newValue):
        self.groupie.hitPoints = oldValue
        from .user import theStore
        theStore.commit()

    def setLocally(self, value):
        original = self.groupie.hitPoints
        self.groupie.hitPoints = int(value)
        from .user import theStore
        theStore.commit()
        return original


class GroupName(WarmText):
    """
    Change the hit points on a groupie
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/GroupName'))
    def __init__(self, monsterGroup, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.monsterGroup = monsterGroup 

    @page.renderer
    def init(self, req, tag):
        gn = self.monsterGroup.name
        tag.fillSlots('value', gn or '')
        return tag

    def rollback(self, failure, oldValue, newValue):
        self.monsterGroup.name = oldValue
        from .user import theStore
        theStore.commit()

    def setLocally(self, value):
        original = self.monsterGroup.name
        self.monsterGroup.name = value
        from .user import theStore
        theStore.commit()
        return original


class GroupieName(WarmText):
    """
    Change the personal name on a groupie
    """
    defaultText = u'Edit name'
    docFactory = loaders.xmlfile(RESOURCE('templates/GroupieName'))
    def __init__(self, groupie, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.groupie = groupie 

    @page.renderer
    def init(self, req, tag):
        gn = self.groupie.name
        tag.fillSlots('value', gn or '')
        return tag

    def rollback(self, failure, oldValue, newValue):
        self.groupie.name = oldValue
        from .user import theStore
        theStore.commit()

    def setLocally(self, value):
        original = self.groupie.name
        self.groupie.name = value
        from .user import theStore
        theStore.commit()
        return original


class GroupieGear(WarmText):
    """
    Change the gear on a groupie
    """
    defaultText = u'Edit gear'
    docFactory = loaders.xmlfile(RESOURCE('templates/GroupieGear'))
    def __init__(self, groupie, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.groupie = groupie 

    @page.renderer
    def init(self, req, tag):
        gn = self.groupie.gear
        tag.fillSlots('value', gn or '')
        return tag

    def rollback(self, failure, oldValue, newValue):
        self.groupie.gear = oldValue
        from .user import theStore
        theStore.commit()

    def setLocally(self, value):
        original = self.groupie.gear
        self.groupie.gear = value
        from .user import theStore
        theStore.commit()
        return original


class GroupieSpells(WarmText):
    """
    Change the spells on a groupie
    """
    defaultText = u'Edit spells'
    docFactory = loaders.xmlfile(RESOURCE('templates/GroupieSpells'))
    def __init__(self, groupie, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.groupie = groupie 

    @page.renderer
    def init(self, req, tag):
        gn = self.groupie.spells
        tag.fillSlots('value', gn or '')
        return tag

    def rollback(self, failure, oldValue, newValue):
        self.groupie.spells = oldValue
        from .user import theStore
        theStore.commit()

    def setLocally(self, value):
        original = self.groupie.spells
        self.groupie.spells = value
        from .user import theStore
        theStore.commit()
        return original


class GroupieAlignment(WarmText):
    """
    Change the alignment on a groupie
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/GroupieAlignment'))
    def __init__(self, groupie, *a, **kw):
        athena.LiveElement.__init__(self, *a, **kw)
        self.groupie = groupie 

    @page.renderer
    def init(self, req, tag):
        gn = self.groupie.alignment
        tag.fillSlots('value', gn or '')
        return tag

    def rollback(self, failure, oldValue, newValue):
        self.groupie.alignment = oldValue
        from .user import theStore
        theStore.commit()

    def setLocally(self, value):
        original = self.groupie.alignment
        self.groupie.alignment = value
        from .user import theStore
        theStore.commit()
        return original


class NPCView(athena.LiveElement):
    """
    The view of an npc in the main page
    """
    docFactory = loaders.xmlfile(RESOURCE('templates/NPC'))
    jsClass = u"Goonmill.NPC"

    def __init__(self, constituent):
        self.constituent = constituent
        athena.LiveElement.__init__(self)

    @page.renderer
    def initialize(self, req, tag):
        tag.fillSlots('monsterName', self.constituent.name)
        return tag
