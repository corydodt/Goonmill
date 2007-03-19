"""The resource structure for Goonmill"""

from nevow import rend, url, loaders, athena

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
        return GoonmillPage()

    def renderHTTP(self, ctx):
        return url.root.child("app")

class GoonmillPage(athena.LivePage):
    docFactory = loaders.stan(['hello'])
