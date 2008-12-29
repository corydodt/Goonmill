"""
A very simple file upload resource
"""

from nevow import (rend, loaders, inevow, url)

from .util import RESOURCE

class FileUploadPage(rend.Page):
    docFactory = loaders.xmlfile(RESOURCE('templates/upload.xhtml'))
    addSlash = True

    def renderHTTP(self, ctx):
        req = inevow.IRequest(ctx)
        arg = lambda s: req.args.get(s, [None])[0]
        if arg('imageUploadType'):
            type = arg('imageUploadType')
            if type == 'url':
                do_url_stuff() # 'imageFileURL': ['http://']
            elif type == 'file':
                import pdb; pdb.set_trace()
                # TODO 'imageFileName': ['']
                # callback here?
            return url.root.child('static').child('uploaddone.xhtml')
        else:
            return rend.Page.renderHTTP(self, ctx)
