"""
Use the history module to format monsters
"""

import unittest
from .. import history
from playtools import query

class HistoryTestCase(unittest.TestCase):
    def test_statblock(self):
        sb = history.Statblock.fromId(379)
        self.assertEqual(sb.get('alignment'), 'Chaotic Evil') 
        self.assertEqual(sb.get('hitDice'), '2d12')

        # just load all the monsters
        monsters = query.allMonsters()
        for monster in monsters:
            exp = [monster.name, None]
            monster = history.Statblock.fromId(monster.id)
            act = [monster.get('name'), monster and None]
            self.assertEqual(exp, act)

    def test_parseFeats(self):
        dbmohrg = query.lookup(u'Mohrg')
        mohrg = history.Statblock.fromMonster(dbmohrg)
        self.assertEqual(mohrg.get('acFeats'), 'Dodge, Mobility')

    def test_oneLine(self):
        """
        Make sure one-line descriptions are correctly formatted
        """
        mohrg = query.lookup(501, query.Monster)
        self.assertEqual(history.oneLineDescription(mohrg),
                u'<<Mohrg>> Chaotic Evil Medium Undead || Init +9 || Darkvision 60 ft., Darkvision 60 ft. Listen +11 Spot +15 || AC 23 (+4 Dex, +9 natural), touch 14, flat-footed 14 || 14d12 HD || Fort +4 Ref +10 Will +9 || 30 ft. (6 squares) || MELEE Slam +12 (1d6+7) melee, and tongue +12 (paralysis) melee || Atk Options Improved grab, paralyzing touch, create spawn || Str 21, Dex 19, Con -, Int 11, Wis 10, Cha 10 || SQ Darkvision 60 ft., undead traits || http://www.d20srd.org/srd/monsters/mohrg.htm'
                )

    def test_statblockSkill(self):
        skillStats = query._allSkillStats()
        for s in skillStats:
            if s is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [s, {}]
            act = [s, history.parseSkills(s) and {}]
            self.assertEqual(exp, act)
            

    def test_statblockFeat(self):
        featStats = query._allFeatStats()
        for f in featStats:
            if f is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [f, []]
            act = [f, history.parseFeats(f) and []]
            self.assertEqual(exp, act)

    def test_hitPoints(self):
        hpStats = query._allHPStats()
        for hp in hpStats:
            if hp is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [hp, None]
            act = [hp, history.parseHitPoints(hp) and None]
            self.assertEqual(exp, act)

    def test_saves(self):
        saveStats = query._allSaveStats()
        for saves in saveStats:
            if saves is None:
                continue

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [saves, []]
            act = [saves, history.parseSaves(saves) and []]
            self.assertEqual(exp, act)

