"""
A very simple file upload resource
"""
from twisted.internet import defer
from twisted.web.client import getPage

from nevow import (rend, loaders, inevow, url)

from .util import RESOURCE
from .userfile import StaticImage, userFolder

class FileUploadPage(rend.Page):
    docFactory = loaders.xmlfile(RESOURCE('templates/upload.xhtml'))
    addSlash = True

    def __init__(self, user=None, *a, **kw):
        self.user = user
        rend.Page.__init__(self, *a, **kw)

    def renderHTTP(self, ctx):
        req = inevow.IRequest(ctx)
        arg = lambda s: req.args.get(s, [None])[0]
        if arg('imageUploadType'):

            def getFileData(type):
                if type == 'url':
                    return getPage(arg('imageFileURL'))
                elif type == 'file':
                    return defer.succeed(arg('imageFileData'))

            type = arg('imageUploadType')
            d = getFileData(type)

            # FIXME - handle errback (413 on upload or 404 on download)

            def gotData(data):
                """
                Thumbnail off the data and save it
                """
                whereto = userFolder(self.user)
                # FIXME - handle not-an-image error
                thumb = StaticImage.fromBytes(data, whereto, 384, 384)
                return url.root.child('static').child('uploaddone.xhtml')

            d.addCallback(gotData)
            return d 
        else:
            return rend.Page.renderHTTP(self, ctx)

