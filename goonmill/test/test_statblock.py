"""
Use the statblock module to format monsters
"""

from twisted.trial import unittest
from .. import statblock
from playtools import fact
from playtools.test.util import pluck

SRD = fact.systems['D20 SRD']
MONSTERS = SRD.facts['monster']

class StatblockTestCase(unittest.TestCase):
    def test_statblockQuick(self):
        """
        Basic properties of the monster can be read
        """
        sb = statblock.Statblock.fromId(379)
        self.assertEqual(sb.get('alignment'), 'Chaotic Evil') 
        self.assertEqual(sb.get('hitDice'), '2d12')

    def test_statblockFromMonster(self):
        """
        We can construct a statblock from an instance of Monster
        """
        monster = MONSTERS[379]
        sb2 = statblock.Statblock.fromMonster(monster)
        self.assertEqual(sb2.get('alignment'), 'Chaotic Evil') 
        self.assertEqual(sb2.get('hitDice'), '2d12')

    def test_parseFeats(self):
        """
        A monster's feats can be read and parsed into a list, and reformatted
        back out
        """
        dbmohrg = MONSTERS[u'Mohrg']
        mohrg = statblock.Statblock.fromMonster(dbmohrg)
        self.assertEqual(mohrg.get('acFeats'), 'Dodge, Mobility')
        self.assertEqual(mohrg.get('feats'), 
            u'Alertness, Dodge, Improved Initiative, Lightning Reflexes, Mobility')

    def test_parseSkills(self):
        """
        A monster's skills can be read and parsed into a list, and reformatted
        back out
        """
        dbmohrg = MONSTERS[u'Mohrg']
        mohrg = statblock.Statblock.fromMonster(dbmohrg)
        self.assertEqual(mohrg.get('skills'), 
                u'Climb +13, Hide +21, Listen +11, Move Silently +21, Spot +15, Swim +9'
                )

    def test_oneLine(self):
        """
        Make sure one-line descriptions are correctly formatted
        """
        mohrg = MONSTERS.lookup(501)
        self.assertEqual(statblock.oneLineDescription(mohrg),
                u'<<Mohrg>> Chaotic Evil Medium Undead || Init +9 || Darkvision 60 ft., Darkvision 60 ft. Listen +11 Spot +15 || AC 23 (+4 Dex, +9 natural), touch 14, flat-footed 14 || 14d12 HD || Fort +4 Ref +10 Will +9 || 30 ft. (6 squares) || MELEE Slam +12 (1d6+7) melee, and tongue +12 (paralysis) melee || Atk Options Improved grab, paralyzing touch, create spawn || Str 21, Dex 19, Con -, Int 11, Wis 10, Cha 10 || SQ Darkvision 60 ft., undead traits || http://www.d20srd.org/srd/monsters/mohrg.htm'
                )

    def test_family(self):
        """
        Monsters' families are correctly extracted
        """
        barghest = statblock.Statblock.fromMonster(MONSTERS[144])
        actual = sorted(pluck(barghest.families, 'label'))
        expected = sorted([u'Outsider', u'Evil', u'Extraplanar', u'Lawful',
            u'Shapechanger'])
        self.assertEqual(actual, expected)


class HugeStatblockTestCase(unittest.TestCase):
    """
    Crude tests that run some of the code on all the monsters
    """
    def test_statblockALL(self):
        # just load all the monsters
        monsters = MONSTERS.dump()
        for monster in monsters:
            exp = [monster.name, None]
            monster = statblock.Statblock.fromId(monster.id)
            act = [monster.get('name'), monster and None]
            self.assertEqual(exp, act)

    def test_statblockSkillALL(self):
        skillStats = [m.skills for m in MONSTERS.dump()]
        for s in skillStats:
            if s is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [s, {}]
            act = [s, statblock.parseSkills(s) and {}]
            self.assertEqual(exp, act)
        #

    def test_statblockFeatALL(self):
        featStats = [m.feats for m in MONSTERS.dump()]
        for f in featStats:
            if f is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [f, []]
            act = [f, statblock.parseFeats(f) and []]
            self.assertEqual(exp, act)

    def test_hitPointsALL(self):
        hpStats = [m.hit_dice for m in MONSTERS.dump()]
        for hp in hpStats:
            if hp is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [hp, None]
            act = [hp, statblock.parseHitPoints(hp) and None]
            self.assertEqual(exp, act)

    def test_savesALL(self):
        saveStats = [m.saves for m in MONSTERS.dump()]
        for saves in saveStats:
            if saves is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [saves, []]
            act = [saves, statblock.parseSaves(saves) and []]
            self.assertEqual(exp, act)

