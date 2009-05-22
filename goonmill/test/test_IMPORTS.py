"""
Sanity check for import names
"""

import unittest

class IMPORTTestCase(unittest.TestCase):
    """
    Just import things and make sure modules weren't deleted
    """
    def test_importStuff(self):
        from ..util import RESOURCE
        RESOURCE
        from ..userfile import StaticImage, userFolder
        StaticImage, userFolder
        from ..fileupload import FileUploadPage
        FileUploadPage
        from ..statblock import Statblock
        Statblock
        from ..resource import Root
        Root
