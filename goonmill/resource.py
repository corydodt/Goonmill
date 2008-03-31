"""
The resource structure for Goonmill

API for building the goonmill page and its fragments.
"""
import random

from nevow import rend, url, loaders, athena, static, guard, page

from twisted.cred.portal import Portal
from twisted.cred.credentials import IAnonymous
from twisted.cred.checkers import AllowAnonymousAccess

from .util import RESOURCE
from .user import Workspace

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
        return ctx.tag


class WorkspaceTitle(athena.LiveElement):
    docFactory = loaders.xmlfile(RESOURCE('templates/WorkspaceTitle'))
    def __init__(self, workspace, *a, **kw):
        self.workspace = workspace
        athena.LiveElement.__init__(self, *a, **kw)

    @page.renderer
    def name(self, req, tag):
        ws = self.workspace
        if ws.name is None:
            ws.name = u"Unnamed Workspace"
            from .user import theStore
            theStore.commit()
        tag.fillSlots('nameValue', ws.name)
        return tag
