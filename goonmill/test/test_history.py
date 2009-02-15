"""
Use the history module to format monsters
"""

import unittest
from .. import history, query

class HistoryTestCase(unittest.TestCase):
    def test_statblock(self):
        sb = history.Statblock.fromId(379)
        self.assertEqual(sb.get('alignment'), 'Chaotic Evil') 
        self.assertEqual(sb.get('hitDice'), '2d12')

        # just load all the monsters
        monsters = query.allMonsters()
        for monster in monsters:
            exp = [monster.name, None]
            act = [monster.name, history.Statblock.fromId(monster.id) and
                    None]
            self.assertEqual(exp, act)


    # tests
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

