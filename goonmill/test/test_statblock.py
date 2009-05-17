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

    def test_noFullAbilities(self):
        """
        The monster with no special qualities has no full ability column to
        parse
        """
        stoneColossus= statblock.Statblock.fromId(13)
        actual = stoneColossus.parseFullAbilities()[1]
        expected = ''
        self.assertEqual(actual, expected)

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

        # no skills, too.
        shrieker = statblock.Statblock.fromId(372)
        self.assertEqual(shrieker.get('skills'), u'-')
        vine = statblock.Statblock.fromId(450)
        self.assertEqual(vine.get('skills'), u'-')

    def test_family(self):
        """
        Monsters' families are correctly extracted
        """
        barghest = statblock.Statblock.fromMonster(MONSTERS[144])
        actual = sorted(pluck(barghest.families, 'label'))
        expected = sorted([u'Outsider', u'Evil', u'Extraplanar', u'Lawful',
            u'Shapechanger'])
        self.assertEqual(actual, expected)

        babau = statblock.Statblock.fromId(165)
        actual = sorted(pluck(babau.families, 'label'))
        expected = sorted([u'Demon', u'Outsider', u'Extraplanar',
            u'Evil', u'Chaotic'])
        self.assertEqual(actual, expected)

    def test_speedFeats(self):
        """
        Monsters with speed feats show them
        """
        triton = statblock.Statblock.fromId(588)
        actual = triton.get('speedFeats')
        expected = u'Ride-by Attack'
        self.assertEqual(actual, expected)

    def test_acFeats(self):
        """
        Monsters with ac feats show them
        """
        atropal = statblock.Statblock.fromId(2)
        actual = atropal.get('acFeats')
        expected = u'Dodge, Mobility'
        self.assertEqual(actual, expected)

    def test_attackOptionFeats(self):
        """
        Monsters with attack option feats show them
        """
        hunter = statblock.Statblock.fromId(56)
        actual = hunter.get('attackOptionFeats')
        expected = u'Blind-Fight, Cleave, Great Cleave, Mounted Combat, Power Attack, Spirited Charge, Trample'
        self.assertEqual(actual, expected)

    def test_rangedAttackFeats(self):
        """
        Monsters with ranged attack feats show them
        """
        harpy = statblock.Statblock.fromId(409)
        actual = harpy.get('rangedAttackFeats')
        expected = u'Manyshot, Rapid Shot'
        self.assertEqual(actual, expected)

    def test_hitPoints(self):
        """
        Critters with odd hit points get shown
        """
        # psicrystals have odd hit points
        psi = statblock.Statblock.fromId(672)
        actual = psi.get('hitPoints')
        expected = u'Special'
        self.assertEqual(actual, expected)

        # regular hit points
        anaxim = statblock.Statblock.fromId(1)
        actual = int(anaxim.get('hitPoints'))
        self.assertTrue(150 < actual < 300, actual)

        # fractional hit dice
        toad = statblock.Statblock.fromId(137)
        actual = int(toad.get('hitPoints'))
        self.assertEqual(actual, 1)

    def test_hitDice(self):
        """
        Odd hit dice get parsed correctly
        """
        psi = statblock.Statblock.fromId(672)
        actual = psi.get('hitDice')
        expected = u"As master's HD (hp 1/2 master's)"
        self.assertEqual(actual, expected)

    def test_specialAC(self):
        """
        Beasties with specialAC show that
        """
        forceDragon = statblock.Statblock.fromId(21)
        actual = forceDragon.get('specialAC')
        expected = u'Deflecting Force'
        self.assertEqual(actual, expected)

    def test_casterLevel(self):
        """
        Beasties with caster level show that
        """
        forceDragon = statblock.Statblock.fromId(21)
        actual = forceDragon.get('casterLevel')
        expected = u'3rd'
        self.assertEqual(actual, expected)

        # no caster level
        anaxim = statblock.Statblock.fromId(1)
        actual = anaxim.get('casterLevel')
        expected = None
        self.assertEqual(actual, expected)

    def test_specialActions(self):
        """
        Beasties with special actions show that
        """
        octopus = statblock.Statblock.fromId(115)
        actual = octopus.get('specialActions')
        expected = u'Ink Cloud, Jet'
        self.assertEqual(actual, expected)

    def test_languages(self):
        """
        Beasties with languages show that
        """
        babau = statblock.Statblock.fromId(165)
        actual = babau.get('languages')
        expected = u'Abyssal, Celestial, Draconic'
        self.assertEqual(actual, expected)

    def test_resistances(self):
        """
        Beasties with resistances show that
        """
        demilich = statblock.Statblock.fromId(16)
        actual = demilich.get('resistances')
        expected = u'Acid 20, Fire 20, Sonic 20, Turn +20'
        self.assertEqual(actual, expected)

        # family resistances
        babau = statblock.Statblock.fromId(165)
        self.assertEqual(babau.get('resistances'), u'Acid 10, Cold 10, Fire 10')

        # no resistances..
        anaxim = statblock.Statblock.fromId(1)
        self.assertEqual(anaxim.get('resistances'), None)

    def test_spellResistance(self):
        """
        Beasties with spell resistance show that
        """
        demilich = statblock.Statblock.fromId(16)
        actual = demilich.get('spellResistance')
        expected = None
        self.assertEqual(actual, expected)
        anaxim = statblock.Statblock.fromId(1)
        actual = anaxim .get('spellResistance')
        expected = u'34'
        self.assertEqual(actual, expected)

    def test_immunities(self):
        """
        Beasties with immunities show that
        """
        demilich = statblock.Statblock.fromId(16)
        actual = demilich.get('immunities')
        expected = u'Death Effects, Mind-Affecting Attacks, Disease, Magic , Paralysis, Poison, Sleep, Stunning, cold, electricity, mind-affecting attacks, polymorph'
        self.assertEqual(actual, expected)

        # none...
        hobgoblin = statblock.Statblock.fromId(413)
        actual = hobgoblin.get('immunities')
        expected = None
        self.assertEqual(actual, expected)

    def test_regeneration(self):
        """
        Beasties with regeneration show that
        """
        atropal = statblock.Statblock.fromId(2)
        actual = atropal.get('regeneration')
        expected = u'20'
        self.assertEqual(actual, expected)

        # none..
        anaxim = statblock.Statblock.fromId(1)
        actual = anaxim.get('regeneration')
        expected = None
        self.assertEqual(actual, expected)

    def test_attackGroups(self):
        """
        Attack groups can be parsed correctly, and cache correctly
        """
        deva = statblock.Statblock.fromId(431)
        actual = deva.get('attackGroups')
        expected = {'melee': ['plus3 heavy mace of disruption +21/+16/+11 (1d8+12 plus stun) melee',
           'slam +18 (1d8+9) melee'], 'ranged': []}
        self.assertEqual(actual, expected)

        # cached
        actual = deva.get('attackGroups')
        self.assertEqual(actual, expected)

    def test_fastHealing(self):
        """
        Beasties with fast healing show that
        """
        anaxim = statblock.Statblock.fromId(1)
        actual = anaxim.get('fastHealing')
        expected = u'15'
        self.assertEqual(actual, expected)

    def test_damageReduction(self):
        """
        Beasties with damage reduction show that
        """
        anaxim = statblock.Statblock.fromId(1)
        actual = anaxim.get('damageReduction')
        expected = u'10/chaotic and epic and adamantine'
        self.assertEqual(actual, expected)

    def test_aura(self):
        """
        Beasties with auras show that
        """
        atropal = statblock.Statblock.fromId(2)
        actual = atropal.get('aura')
        expected = u'negative energy'
        self.assertEqual(actual, expected)

        # odd auras..
        phane = statblock.Statblock.fromId(8)
        actual = phane.get('aura')
        expected = u'Null Time Field'
        self.assertEqual(actual, expected)

    def test_senses(self):
        """
        Beasties with senses show that
        """
        babau = statblock.Statblock.fromId(165)
        actual = babau.get('senses')
        expected = u'Darkvision 60 ft., Telepathy 100 ft.'
        self.assertEqual(actual, expected)

        # no senses?
        locathah = statblock.Statblock.fromId(463)
        actual = locathah.get('senses')
        expected = u'-'
        self.assertEqual(actual, expected)

        # non-ranged senses
        forceDragon = statblock.Statblock.fromId(21)
        actual = forceDragon.get('senses')
        expected = u'Blindsense 60 ft., Darkvision 120 ft., Keen Senses, Low-Light Vision'
        self.assertEqual(actual, expected)

    def test_vulnerabilities(self):
        """
        Beasties with vulnerabilities show that
        """
        phaethon = statblock.Statblock.fromId(7)
        actual = phaethon.get('vulnerabilities')
        expected = [u'cold']
        self.assertEqual(actual, expected)

        # none..
        anaxim = statblock.Statblock.fromId(1)
        actual = anaxim.get('vulnerabilities')
        expected = []
        self.assertEqual(actual, expected)

    def test_oddAlignment(self):
        """
        Monsters with no or odd alignment
        """
        ape = statblock.Statblock.fromId(83)
        actual = ape.formatAlignment()
        expected = 'None'
        self.assertEqual(actual, expected)

        leshay = statblock.Statblock.fromId(62)
        actual = leshay.formatAlignment()
        expected = 'Any'
        self.assertEqual(actual, expected)


class HugeStatblockTestCase(unittest.TestCase):
    """
    Crude test that runs some of the code on all the monsters
    """
    def test_statblockALL(self):
        # just load all the monsters
        monsters = MONSTERS.dump()
        for monster in monsters:
            exp = [monster.name, None]
            monster = statblock.Statblock.fromId(monster.id)
            act = [monster.get('name'), monster and None]
            self.assertEqual(exp, act)
