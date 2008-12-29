"""
Utility classes for dealing with user files in the filesystem
"""
import os
import hashlib
from cStringIO import StringIO

from PIL import Image
from .util import RESOURCE


class ImageDecodeError(Exception):
    """
    The image could not be decoded
    """


class StaticImage(object):
    """A managed image class, for finding/creating thumbnails"""
    def __init__(self, url):
        self.url = url
        self.file = RESOURCE(self.url.lstrip("/"))

    def scaledImageSize(self, maxWidth, maxHeight):
        """
        The size the image would be if you scaled it to fit within a box
        'maxWidth'x'maxHeight' with no change of aspect ratio.

        If the image already fits in both dimensions, it will not be resized.
        """
        mw, mh = map(float, [maxWidth, maxHeight])
        # PIL cannot read all image types, so try/except to punt
        try:
            filedata = open(self.file, 'r')
            original = Image.open(filedata)
            w, h = original.size
            scaleW = mw / w
            scaleH = mh / h
            if scaleW <= scaleH:
                return scaleW * w, scaleW * h
            else:
                return scaleH * w, scaleH * h
        except IOError:
            return 0,0

    def getThumbnailUrl(self, maxWidth, maxHeight):
        """
        Return a url to a thumbnail of the specified dimensions.
        If it already exists in the filesystem, just return it, otherwise
        create it.
        """
        if self.file is None:
            return None

        def repackage(s):
            if '.' in s:
                left, ext = s.rsplit('.', 1)
                return "%s_%sx%s.%s" % (left, maxWidth, maxHeight, ext)
            else:
                return "%s_%sx%s" % (s, maxWidth, maxHeight)

        needFilename = repackage(self.file)
        if not os.path.exists(needFilename):
            filedata = open(self.file, 'r')
            thumb = self.thumbnail(filedata, maxWidth, maxHeight, needFilename)
            if thumb is None:
                return None
        return repackage(self.url)

    @classmethod
    def fromBytes(cls, bytes, folder, maxWidth, maxHeight):
        """
        New StaticImage created by converting the string 'bytes' into a PNG of
        'maxWidth'x'maxHeight' dimensions and dropping the result into 'folder'.
        """
        io = StringIO(bytes)
        newfile = cls.thumbnail(io, maxWidth, maxHeight)
        thumb = newfile.read()
        hex = hashlib.md5(thumb).hexdigest()
        staticImage = cls('%s/%s.png' % (folder, hex))
        open(staticImage.file, 'w').write(thumb)
        return staticImage

    @staticmethod
    def thumbnail(stream, maxWidth, maxHeight, outFile=None):
        """
        Return a string of thumbnail data
        """
        # PIL can't thumbnail every identifiable kind of
        # image, so just punt if it fails to update.
        try:
            original = Image.open(stream)
            thumb = original.copy()
            thumb.thumbnail((maxWidth,maxHeight), Image.ANTIALIAS)
            if outFile is None:
                _tempfile = StringIO()
            else:
                _tempfile = open(outFile, 'w')
            thumb.save(_tempfile, 'PNG', optimize=True)
            _tempfile.seek(0)
            return _tempfile

        except IOError:
            raise ImageDecodeError("Couldn't figure out this image.  Are you sure it's an image?")


def userFolder(user):
    """
    Return the folder where a particular user's files will be stored in the
    filesystem
    """
    if user is None:
        return u'/static/upload'
    return user.folder
