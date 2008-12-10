"""Badly named module that contains the driving code for the rendering."""

from pydoctor.nevowhtml import NevowWriter
from hypy.nevowhtml import pages
from nevow import flat

class CoryWriter(NevowWriter):

    def writeDocsForOne(self, ob, fobj):
        if not ob.isVisible:
            return
        # brrrrrrrr!
        d = pages.__dict__
        for c in ob.__class__.__mro__:
            n = c.__name__ + 'Page'
            if n in d:
                pclass = d[n]
                break
        else:
            pclass = pages.CommonPage
        self.system.msg('html', str(ob), thresh=1)
        page = pclass(ob)
        self.written_pages += 1
        self.system.progress('html', self.written_pages, self.total_pages, 'pages written')
        fobj.write(flat.flatten(page))
