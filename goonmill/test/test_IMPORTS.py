"""
Sanity check for import names
"""

import unittest

class IMPORTTestCase(unittest.TestCase):
    """
    Just import things and make sure modules weren't deleted
    """
    def test_importUtil(self):
        from ..util import RESOURCE
        RESOURCE

    def test_importUserfile(self):
        from ..userfile import StaticImage, userFolder
        StaticImage, userFolder

    def test_importFileupload(self):
        from ..fileupload import FileUploadPage
        FileUploadPage

    def test_importStatblock(self):
        from ..statblock import Statblock
        Statblock

    def test_importResource(self):
        from ..resource import Root
        Root

    def test_importAuth(self):
        from ..auth import CookieRealm
        CookieRealm

    def test_importWebserver(self):
        from ..webserver import WebServer
        WebServer
