"""
Test access to the triplestore
"""

import unittest
import string

import re

from .. import rdfquery

import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

class RDFQueryTestCase(unittest.TestCase):
    def setUp(self):
        if rdfquery.db is None:
            rdfquery.openDatabase()

    def test_feat(self):
        """
        Verify that attributes of the feat triples are accessible
        """
        def feat(k):
            return rdfquery.Feat(db=rdfquery.db,
                    key=getattr(rdfquery.FEAT, k))

        heavy = feat('armorProficiencyHeavy')

        exp = '.*Armor Proficiency \(medium\).*'
        act = heavy.prerequisiteText

        self.failIfEqual(re.match(exp, str(act)), None, "%s != %s" % (exp, act))
        self.assertEqual(heavy.stackable, False)

    def test_skill(self):
        """
        Verify that attributes of the skill triples are accessible
        """
        cha = rdfquery.Ability(db=rdfquery.db, 
                key=rdfquery.CHAR.cha)
        self.assertEqual(str(cha.label), 'Cha')
        def skill(k):
            return rdfquery.Skill(db=rdfquery.db,
                    key=getattr(rdfquery.SKILL, k))

        dipl = skill('diplomacy')

        self.assertEqual(str(dipl.keyAbility[0].label), 'Cha')
        # TODO - should be able to get an integer here straight from the API,
        # oh well
        self.assertEqual(int(dipl.synergy[0].bonus), 2)

    def test_family(self):
        """
        Verify that attributes of the family triples are accessible
        """
        def family(k):
            return rdfquery.Family(db=rdfquery.db,
                    key=getattr(rdfquery.FAM, k))

        self.assertEqual(len(family('devil').languages), 3)
        self.assertEqual(str(family('ooze').combatMechanics[0].label),
                'Not subject to critical hits')
        und = family('undead')
        self.assertEqual(str(und.specialQualities[0].comment), 
            'Cannot be raised or resurrected.')
        self.assertEqual(len(family('construct').combatMechanics), 8)
        fey = family('fey')
        self.assertEqual(str(fey.senses[0].label), 'Low-Light Vision')
