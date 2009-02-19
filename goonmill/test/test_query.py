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

    def test_oneLine(self):
        """
        Make sure one-line descriptions are correctly formatted
        """
        fireball = query.lookup(294, query.Spell)
        self.assertEqual(fireball.oneLineDescription(), 
                u'<<Fireball>> Evocation || Level: Sorcerer/Wizard 3 || Casting Time: 1 standard action || VSM || Range: Long (400 ft. + 40 ft./level) || Area: 20-ft. -radius spread || Duration: Instantaneous || Save: Reflex half || 1d6 damage per level, 20-ft. radius. || http://www.d20srd.org/srd/spells/fireball.htm',
                )
        cswm = query.lookup(205, query.Spell)
        actual = cswm.oneLineDescription()
        exp = u'<<Cure Serious Wounds, Mass>> Conjuration (Healing) || Level: Cleric 7, Druid 8 || Casting Time: 1 standard action || VS || Range: Close (25 ft. + 5 ft./2 levels) || Target: One creature/level, no two of which can be more than 30 ft. apart || Duration: Instantaneous || Save: Will half (harmless) or Will half; see text || Cures 3d8 damage +1/level for many creatures. || http://www.d20srd.org/srd/spells/cureSeriousWoundsMass.htm'
        self.assertEqual(actual, exp)

    def test_srdReferenceURL(self):
        cswm = query.lookup(205, query.Spell)
        self.assertEqual('http://www.d20srd.org/srd/spells/cureSeriousWoundsMass.htm',
                query.srdReferenceURL(cswm))
        animusBlast = query.lookup(15, query.Spell)
        self.assertEqual('http://www.d20srd.org/srd/epic/spells/animusBlast.htm',
                query.srdReferenceURL(animusBlast))

