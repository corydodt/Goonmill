from nevow import athena, loaders, tags as T, flat

from goonmill.util import RESOURCE
from goonmill import dice

class DiceSandboxPage(athena.LivePage):
    # FIXME - for now, just use the goonmill page
    docFactory = loaders.xmlfile(RESOURCE('templates/goonmillpage.xhtml'))
    addSlash = 1
    
    def render_all(self, ctx, data):
        d = DiceSandbox()
        d.setFragmentParent(self)

        return ctx.tag[d, ]


class DiceSandbox(athena.LiveElement):
    """A playground for rolling dice"""
    docFactory = loaders.xmlfile(RESOURCE("elements/DiceSandbox"))
    jsClass = u'Goonmill.DiceSandbox'

    def onQuerySubmit(self, query):
        rolled = [r.sum() for r in dice.parse(query)]
        ret = []
        if len(list(rolled)) >= 1:
            rolled = map(str, rolled)
            ret.append(T.div["Unsorted: " + ", ".join(rolled)])
            rolled.sort()
            rolled.reverse()
            ret.append(T.div["Sorted: " + ", ".join(rolled)])
        ret = unicode(flat.flatten(ret))
        return ret

    athena.expose(onQuerySubmit)



