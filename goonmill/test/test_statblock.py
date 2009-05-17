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

    def test_oneLine(self):
        """
        Make sure one-line descriptions are correctly formatted
        """
        anaxim = MONSTERS.lookup(1)
        expected = u'<<Anaxim>> Lawful Neutral Medium Construct || Init +7 (Dex) || Darkvision 60 ft., Low-Light Vision Listen +0 Spot +0 || AC 37 (+7 Dex, +20 natural), touch 17, flat-footed 30 || 38d10 HD || Fort +12 Ref +19 Will +17 || 60 ft., fly 200 ft. (perfect) || MELEE 2 spinning blades +43 (2d6+12/19-20 (plus 1d6 on critical)) melee, and 2 slams +35 (2d6+6) melee, and shocking touch +35 (2d6+6) melee RANGED electricity ray +35 (10d6 electricity) ranged, and 6 spikes +30 (2d6+12) ranged (120 ft. range increment) || Atk Options Rend 4d6+18, sonic blast, spell-like abilities, summon iron golem || Spell-Like: <div level="8" topic="Spell-Like Abilities"><p><b>Spell-Like Abilities:</b> At will-<i>greater dispel magic</i>,  <i>displacement</i> (DC 18),  <i>greater invisibility</i> (DC 19),  <i>ethereal jaunt</i>. Caster level 22nd. The save DCs are Charisma-based.</p>\n</div> || Str 35, Dex 25, Con -, Int 10, Wis 20, Cha 20 || SQ Abomination traits, magic immunity, construct traits, fast healing 15, spell resistance 34, damage reduction 10/chaotic and epic and adamantine || http://www.d20srd.org/srd/epic/monsters/anaxim.htm'
        self.assertEqual(statblock.oneLineDescription(anaxim), expected)
        mohrg = MONSTERS.lookup(501)
        expected = u'<<Mohrg>> Chaotic Evil Medium Undead || Init +9 || Darkvision 60 ft. Listen +11 Spot +15 || AC 23 (+4 Dex, +9 natural), touch 14, flat-footed 14 || 14d12 HD || Fort +4 Ref +10 Will +9 || 30 ft. (6 squares) || MELEE Slam +12 (1d6+7) melee, and tongue +12 (paralysis) melee || Atk Options Improved grab, paralyzing touch, create spawn || Str 21, Dex 19, Con -, Int 11, Wis 10, Cha 10 || SQ Darkvision 60 ft., undead traits || http://www.d20srd.org/srd/monsters/mohrg.htm'
        self.assertEqual(statblock.oneLineDescription(mohrg), expected)

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

        anaxim = statblock.Statblock.fromId(1)
        actual = int(anaxim.get('hitPoints'))
        self.assertTrue(150 < actual < 300, actual)

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

        # no resistances..
        shrieker = statblock.Statblock.fromId(372)
        self.assertEqual(shrieker.get('skills'), u'-')

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

    ## need to test: update, updateHandler,
    ## parseFeats with none, parseSkills/formatSkills with none,
    ## cached attackGroups, setCount/Label/Alignment/Spells/Spellbook


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
        for m in MONSTERS.dump():
            s = m.skills
            if s is None:
                continue

            sb = statblock.Statblock.fromMonster(m)

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [s, {}]
            act = [s, sb.parseSkills() and {}]
            self.assertEqual(exp, act)
        #

    def test_statblockFeatALL(self):
        for m in MONSTERS.dump():
            f = m.feats
            if f is None:
                continue

            sb = statblock.Statblock.fromMonster(m)

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [f, []]
            act = [f, sb.parseFeats() and []]
            self.assertEqual(exp, act)

    def test_hitPointsALL(self):
        for m in MONSTERS.dump():
            hp = m.hit_dice
            if hp is None:
                continue

            sb = statblock.Statblock.fromMonster(m)

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [hp, None]
            act = [hp, sb.parseHitPoints() and None]
            self.assertEqual(exp, act)

    def test_savesALL(self):
        for m in MONSTERS.dump():
            saves = m.saves
            if saves is None:
                continue

            sb = statblock.Statblock.fromMonster(m)

            # just run the code - embed the stat into the assert so we can
            # read it.
            exp = [saves, []]
            act = [saves, sb.parseSaves() and []]
            self.assertEqual(exp, act)

