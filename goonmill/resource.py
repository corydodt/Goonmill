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
from .user import Workspace
from . import search

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
        title = WorkspaceTitle(self.workspace)
        title.setFragmentParent(self)
        ctx.tag.fillSlots('titleEdit', title)

        cl = ConstituentList(self.workspace)
        cl.setFragmentParent(self)
        ctx.tag.fillSlots('constituentList', cl)

        search = BasicSearch()
        search.setFragmentParent(self)
        ctx.tag.fillSlots('basicSearch', search)

        mainActions = MainActions()
        mainActions.setFragmentParent(self)
        ctx.tag.fillSlots('mainActions', mainActions)

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

    def validate(self, value):
        """
        Simplest DOS-prevention.. limit length.  Adjust if necessary in
        subclasses.
        """
        return len(value) < 2000


class WorkspaceTitle(WarmText):
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


def trunc(s, n):
    """
    s, truncated to n, with "..."
    """
    assert n >= 4
    if len(s) > n:
        s = s[:n-3]
        return s + '...'
    return s


class ConstituentList(athena.LiveElement):
    docFactory = loaders.xmlfile(RESOURCE('templates/ConstituentList'))
    jsClass = u'Goonmill.ConstituentList'

    def __init__(self, workspace, *a, **kw):
        page.Element.__init__(self, *a, **kw)
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
            pat.fillSlots('constituentName', trunc(c.name, 14))
            pat.fillSlots('constituentDetail', trunc(c.briefDetail(), 14))
            pat.fillSlots('constituentId', c.id)
            tag[pat]
        return tag

    @athena.expose
    def removeConstituent(self, id):
        from .user import theStore, Constituent as C
        constituent = theStore.get(C, id)
        assert constituent in self.workspace.constituents

        if constituent.isLibraryKind(): 
            constituent.workspaceId = None
        else:
            theStore.remove(constituent)
        theStore.commit()
        return u'removed'
        

class MainActions(athena.LiveElement):
    """
    The links in the top-left bar that create new things.
    """
    jsClass = u'Goonmill.MainActions'
    docFactory = loaders.xmlfile(RESOURCE('templates/MainActions'))
    

class BasicSearch(athena.LiveElement):
    docFactory = loaders.xmlfile(RESOURCE('templates/BasicSearch'))
    jsClass = u"Goonmill.BasicSearch"

    @athena.expose
    def searched(self, searchTerms):
        terms = searchTerms.split()
        self.lastFound = search.find(terms)
        return [(t.name, int(t.score * 100)) for t in self.lastFound]
