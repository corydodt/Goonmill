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
        from ..userfile import StaticImage, userFolder
        from ..fileupload import FileUploadPage
        from ..history import Statblock
        from ..rdfquery import allFamilies, allSpecialActions, allSpecialAC, allAuras
        from ..resource import Root
