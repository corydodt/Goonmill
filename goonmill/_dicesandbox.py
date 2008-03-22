from twisted.python import log

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
    docFactory = loaders.xmlfile(RESOURCE("templates/DiceSandbox"))
    jsClass = u'Goonmill.DiceSandbox'

    def onQuerySubmit(self, query):
        rolled = [r.sum() for r in dice.parse(query)]
        ret = []
        if len(list(rolled)) >= 1:
            sRolled = map(str, rolled)
            _s = ", ".join(sRolled)
            ret.append(T.div[T.strong["Unsorted"], " ", _s])
            log.msg("    *Unsorted %s* " % (query,), _s, system="*")

            ret.append(T.hr)

            sRolled = reversed(sorted(sRolled, key=int))
            _s = ", ".join(sRolled)
            log.msg("    *Sorted* ", _s, system="*")
            ret.append(T.div[T.strong["Sorted"], " ", _s])

        ret = unicode(flat.flatten(ret))
        return ret

    athena.expose(onQuerySubmit)



