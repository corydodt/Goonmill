"""
Use the history module to format monsters
"""

import unittest
from .. import query

class QueryTestCase(unittest.TestCase):
    def test_lookup(self):
        def test(n,k,s):
            self.assertEqual(
                    query.lookup(n, k).name,
                    s)

        test(10, query.Monster, u'Behemoth Eagle')
        test(10, query.Spell, u'Surelife')
        test(10, query.Skill, u'Diplomacy')
        test(10, query.Feat, u'Jack of all Trades')

    def test_thingLists(self):
        """
        Verify that we are retrieving the right number of things from the
        database with our all* methods
        """
        ms = query.allMonsters()
        ss = query.allSpells()
        self.assertEqual(len(ms), 681)
        self.assertEqual(len(ss), 699)
        self.assertEqual(ms[9].name, u'Behemoth Eagle')
        self.assertEqual(ss[9].name, u'Surelife')
