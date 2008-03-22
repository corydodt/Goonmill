"""
The resource structure for Goonmill

API for building the goonmill page and its fragments.
"""
from nevow import rend, url, loaders, athena, static

from goonmill.util import RESOURCE

class Root(rend.Page):
    """
    Adds child nodes for things common to anonymous and logged-in root
    resources.
    """
    addSlash = True  # yeah, we really do need this, otherwise 404 on /

    def child_static(self, ctx):
        return static.File(RESOURCE('static'))

    def child_app(self, ctx):
        return WorkspacePage()

    def renderHTTP(self, ctx):
        return url.root.child("app")


class WorkspacePage(athena.LivePage):
    docFactory = loaders.xmlfile(RESOURCE('templates/workspace.xhtml'))
    addSlash = 1

