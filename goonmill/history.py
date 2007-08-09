"""The history of statblocks for this session"""

import re

from goonmill import (query, dice, diceparser, skillparser, featparser,
        saveparser, attackparser, fullabilityparser, specialparser, rdfquery)

class History(object):
    """
    A container for all the statblocks we have generated so far in this session
    """
    def __init__(self):
        self.result = None
        self.statblocks = []
        self.pending = []

    def setView(self, view):
        """
        Set the output result element, which will be notified when I change.
        """
        self.view = view

    def addStatblock(self, statblock):
        self.statblocks.append(statblock)
        self.pending.append(statblock)
        self.view.historyUpdated(self)

    def pendingStatblocks(self):
        return self.pending

    def unpendStatblocks(self, statblocks):
        self.pending = list(set(self.pending) - set(statblocks))


hpParser = re.compile(r'(\S+)\s[^(]*\(([\d,]+) hp\)')

class Statblock(object):
    """
    A representation of one statblock; a configured monster that has had
    its hit points generated and labels set up.
    """
    def __init__(self, id):
        self.id = id
        self.monster = query.lookup(id)
        self._count = 1
        self._label = ''
        self.skills = self.parseSkills()
        self.feats = self.parseFeats()

        parsedFullAbilities = self.parseFullAbilities()
        self.overrides = { # when .get() is called, these will be looked up
                           # first and possibly called
                'hitPoints': self.hitPoints,
                'hitDice': self.hitDice,
                'count': self._count,
                'label': self._label,
                'specialAC': self.specialAC,
                'acFeats': lambda: self.formatFeats(self.acFeats),
                'speedFeats': lambda: self.formatFeats(self.speedFeats),
                'attackOptionFeats': lambda: self.formatFeats(self.attackOptionFeats),
                'rangedAttackFeats': lambda: self.formatFeats(self.rangedAttackFeats),
                'listen': '+0', # may be set again, down below
                'spot': '+0', # may be set again, down below
                'alignment': self.formatAlignment,
                'attackGroups': self.attackGroups,
                'fullAbilities': parsedFullAbilities[0],
                'casterLevel': self.casterLevel,
                'spells': self.spells,
                'spellLikeAbilities': parsedFullAbilities[1],
                'spellResistance': self.spellResistance,
                'languages': self.languages,
                'aura': self.aura,
                'fastHealing': self.fastHealing,
                'regeneration': self.regeneration,
                'damageReduction': self.damageReduction,
                'senses': self.senses,
                'immunities': self.immunities,
                'resistances': self.resistances,
                'vulnerabilities': self.vulnerabilities,
                'skills': self.formatSkills,
                'specialActions': self.specialActions,
                }
        savesDict = self.parseSaves()
        for k in savesDict:
            self.overrides[k] = str(savesDict[k])

        ## self.fullAbilities = self.parseFullAbilities()

        listen = self.skills.get('Listen', None)
        if listen is not None: self.overrides['listen'] = listen[7:]

        spot = self.skills.get('Spot', None)
        if spot is not None: self.overrides['spot'] = spot[5:]

        self._handler = None
        self._parsedHitDice = None

        self._parsedSpecialQualities = self.parseSpecialQualities()

        self.determineFamilies()

    def specialAC(self):
        specArmors = rdfquery.allSpecialAC()

        extraArmors = []
        for q in self._parsedSpecialQualities:
            qname = (q.name.lower() if q.name is not None else '')
            if qname in specArmors:
                extraArmors.append(specArmors[qname].label)
            
        extraArmors = ", ".join(extraArmors)

        return extraArmors

    def spells(self):
        return "spells..."

    def casterLevel(self):
        for q in self._parsedSpecialQualities:
            if q.level:
                return q.level

        return None

    def determineFamilies(self):
        """From several of the monster's attributes, compute its families."""
        knownFamilies = rdfquery.allFamilies()
        foundFamilies = set()

        _f = self.monster.family.title()
        if _f in knownFamilies:
            foundFamilies.add(knownFamilies[_f])

        _t = self.monster.type
        if _t in knownFamilies:
            foundFamilies.add(knownFamilies[_t])

        _d = self.monster.descriptor
        if _d is not None:
            for descriptor in _d.split(', '):
                if _d in knownFamilies:
                    foundFamilies.add(knownFamilies[_d])

        for q in self._parsedSpecialQualities:
            if q.type == 'family':
                what = q.what.title()
                if what in knownFamilies:
                    foundFamilies.add(knownFamilies[what])

        self.families = sorted(foundFamilies)

    def update(self, attribute, newValue):
        """I will call this to notify handlers ot changed attributes"""
        if self._handler is None:
            return

        return self._handler(attribute, newValue)

    def updateHandler(self, handler):
        """
        Call with a function with the signature: handler(attribute, newValue)

        It will be called when an attribute of the statblock changes
        """
        self._handler = handler

    alignmentRx = re.compile(r'Always (.*)')

    def formatAlignment(self):
        s = self.monster.alignment

        if s is None:
            return 'None'

        matched = self.alignmentRx.match(s)
        if matched is not None:
            return matched.group(1).title()
        return s

    def parseFullAbilities(self):
        return parseFullAbilities(self.monster.full_text)

    def parseSpecialQualities(self):
        return parseSpecialQualities(self.monster.special_qualities)

    def parseFeats(self):
        return parseFeats(self.monster.feats)

    def parseSkills(self):
        return parseSkills(self.monster.skills)

    def formatSkills(self):
        if self.skills == {}:
            return '-'
        return ', '.join(sorted(self.skills.values()))

    def parseSaves(self):
        return parseSaves(self.monster.saves)

    def formatFeats(self, callable):
        featList = callable()
        return ', '.join([f.name for f in featList])

    def acFeats(self):
        """List of feats that can appear next to AC"""
        return [f for f in self.feats if f.dbFeat.is_ac_feat]

    def speedFeats(self):
        """List of feats that can appear next to movement"""
        return [f for f in self.feats if f.dbFeat.is_speed_feat]

    def specialActionFeats(self):
        """List of feats that can appear next to special actions"""
        return [f for f in self.feats if f.dbFeat.is_special_action_feat]

    def specialActions(self):
        """All special actions as a string"""
        specActions = rdfquery.allSpecialActions()

        extraActions = []
        for q in self._parsedSpecialQualities:
            qname = (q.name.lower() if q.name is not None else '')
            if qname in specActions:
                extraActions.append(specActions[qname].label)
            
        feats = self.formatFeats(self.specialActionFeats)
        extraActions = ", ".join(extraActions)

        feats = (feats + ", " if feats and extraActions else '')

        return feats + extraActions

    def attackOptionFeats(self):
        """List of feats that can appear next to attack options"""
        return [f for f in self.feats if f.dbFeat.is_attack_option_feat]

    def rangedAttackFeats(self):
        """List of feats that can appear next to ranged attacks""" 
        return [f for f in self.feats if f.dbFeat.is_ranged_attack_feat]

    def hitPoints(self):
        """
        @return: A string of multiple hit points
        """
        if self._parsedHitDice is None:
            self._parsedHitDice = self.parseHitPoints()

        hplist = []

        # STILL None.. (i.e. no valid dice expression)
        if self._parsedHitDice is None: 
            hplist = ['Special'] * self._count
        else:
            for n in range(self._count):
                rolled = list(dice.roll(self._parsedHitDice))
                assert len(rolled) == 1, "Too many repeats in this expression - a monter may have only one hit dice expression with no repeats!"
                hplist.append(rolled[0].sum())

            # minimum of 1hp for a monster
            for n, hp in enumerate(hplist):
                if hp < 1: 
                    hplist[n] = 1

        return ', '.join(map(str, hplist))

    def languages(self):
        """Return the languages a creature knows, determined by inspecting
        creature's families.
        """
        ret = set()

        for f in self.families:
            for l in f.languages:
                ret.add(l.label)

        return ', '.join(sorted(ret)) or '-'

    def resistances(self):
        """Return the creature's notable resistances"""
        # use a dict; we're going to load resistances from the family first
        # and then override them from the monster's specialqualities stat
        ret = {}

        for f in self.families:
            for s in f.resistances:
                label = s.attackEffect[0].label
                amt = s.amount
                ret[label] = "%s %s" % (label, amt)

        for q in self._parsedSpecialQualities:
            if q.type == 'resistance':
                ret[q.what.title()] = "%s %s" % (q.what.title(), q.amount)

        # spell resistance is covered elsewhere.
        if 'Spell' in ret: del ret['Spell']

        if len(ret) > 0:
            return ', '.join(sorted(ret.values()))
        return None

    def immunities(self):
        """Return the creature's notable immunities"""
        # use a dict; we're going to load immunities from the family first
        # and then override them from the monster's specialqualities stat
        ret = {}

        for f in self.families:
            for s in f.immunities:
                ret[s.label] = s.label

        for q in self._parsedSpecialQualities:
            if q.type == 'immunity':
                ret[q.what.title()] = q.what

        if len(ret) > 0:
            return ', '.join(sorted(ret.values()))
        return None

    def vulnerabilities(self):
        """Return the creature's notable vulnerabilities"""
        # use a dict; we're going to load vulnerabilities from the family first
        # and then override them from the monster's specialqualities stat
        ret = {}

        for f in self.families:
            for s in f.vulnerabilities:
                ret[s.label] = s.label

        for q in self._parsedSpecialQualities:
            if q.type == 'vulnerability':
                ret[q.what.title()] = q.what

        if len(ret) > 0:
            return sorted(ret.values())
        return []

    def senses(self):
        """Return the creature's notable senses"""
        # use a dict; we're going to load senses from the family first
        # and then override them from the monster's specialqualities stat
        ret = {}

        for f in self.families:
            for s in f.senses:
                if s.range:
                    ret[s.label] = "%s %s" % (s.label, s.range)
                else:
                    ret[s.label] = s.label

        for q in self._parsedSpecialQualities:
            if q.type == 'sense':
                if q.range:
                    ret[q.name.title()] = "%s %s" % (q.name, q.range)
                else:
                    ret[q.name.title()] = q.name

        if len(ret) > 0:
            return ', '.join(sorted(ret.values()))
        return '-'

    def spellResistance(self):
        """Return the creature's spell resistance, if any"""
        for q in self._parsedSpecialQualities:
            if q.type == 'resistance' and q.what == 'spell':
                return q.amount

    def fastHealing(self):
        """Return the creature's fast healing, if any"""
        for q in self._parsedSpecialQualities:
            if q.type == 'fastHealing':
                return q.amount

    def regeneration(self):
        """Return the creature's regeneration, if any"""
        for q in self._parsedSpecialQualities:
            if q.type == 'regeneration':
                return q.amount

    def damageReduction(self):
        """Return the creature's damage reduction, if any"""
        for q in self._parsedSpecialQualities:
            if q.type == 'damageReduction':
                return q.amount

    def aura(self):
        """Return the creature's aura, if any"""
        all = rdfquery.allAuras()

        ret = []
        for q in self._parsedSpecialQualities:
            if q.type == 'aura':
                ret.append(q.what)

        for q in self._parsedSpecialQualities:
            qname = (q.name.lower() if q.name else '')
            if qname in all:
                ret.append(all[qname].label)

        return ', '.join(sorted(ret)) or None

    def attackGroups(self):
        """
        @return: A dict:list of attack groups, formatted.  The keys in the
        dict will be 'melee' and 'ranged' and the values will be a list of
        attack options for one of those two keys.
        """
        ret = {'melee':[], 'ranged':[]}

        if getattr(self, '_parsedAttackGroups', None) is None:
            options = self._parsedAttackGroups = self.parseAttackGroups()
        else:
            options = self._parsedAttackGroups

        for option in options:
            forms = option.attackForms
            # we assume (and for all the entries in the existing database,
            # this is true) that an option can either have *all* ranged
            # attacks, or *all* melee attacks, not some mixture that can be
            # used simultaneously.
            optionType = forms[0].type # melee or ranged

            ret[optionType].append(', and '.join(map(str, forms)))

        return ret

    def hitDice(self):
        """
        @return: The hit dice expression for the monster as a string.
        """
        if self._parsedHitDice is None:
            self._parsedHitDice = self.parseHitPoints()

        if self._parsedHitDice is None:
            return self.monster.hit_dice
        return str(self._parsedHitDice[0])

    def parseHitPoints(self):
        """Roll hit points for one monster of this type"""
        return parseHitPoints(self.monster.hit_dice)

    def parseAttackGroups(self):
        """Get the attack options dict"""
        return parseAttackGroups(self.monster.full_attack)

    def get(self, attribute):
        """
        Retrieve an attribute as a string or int, first by looking it up in my
        own property list (which might have been modified from the server) and
        second by looking it up in the monster's ORM object.
        """
        if attribute in self.overrides:
            att = self.overrides[attribute]
            if callable(att):
                return att()
            assert isinstance(att, 
                    (unicode, str, int)), "%r ain't int or string" % (att,)
            return att
        return getattr(self.monster, attribute)

    def setCount(self, count):
        count = int(count)
        self.overrides['count'] = count
        self._count = count
        hp = self.hitPoints()
        self.update('hp', hp)
 
    def setLabel(self, label):
        self.overrides['label'] = label

    def setAlignment(self, alignment):
        self.overrides['alignment'] = alignment


def parseFeats(featStat):
    """All feats of the monster, as a list of Feat."""
    ret = []
    # check this before trying to parse
    if featStat is None:
        return ret

    parsed = featparser.parseFeats(featStat)[0]

    for item in parsed:
        item.dbFeat = query.lookupFeat(item.name)
        ret.append(item)

    return ret

def parseHitPoints(hpStat):
    """Hit points of the monster as a ParseResults object (should be a
    StatblockHitPoints object!)
    """
    m = hpParser.match(hpStat)
    if m is None:
        # monster has very non-standard hit dice (e.g. Psicrystal)
        return 

    p = lambda s: diceparser.parseDice(s)
    # try parsing the first group as a dice expression. if that fails,
    # return the second group as non-random hit points.
    try:
        _parsed = p(m.group(1))
        return _parsed
    except RuntimeError:
        return p(m.group(2))

def parseSkills(skillStat):
    """All skills of the monster as a dict of strings"""
    # check this before trying to parse
    if skillStat is None:
        return {}

    parsed = skillparser.parseSkills(skillStat)[0]

    return dict([(item.skillName, str(item)) for item in parsed])

def parseSaves(saveStat):
    """Fort, Ref and Will saves as dict of StatblockSave objects"""
    return saveparser.parseSaves(saveStat)[0]

def parseAttackGroups(attackStat):
    """All grouped attack options as strings"""
    return attackparser.parseAttacks(attackStat)[0]

def parseFullAbilities(fullTextStat):
    """All full ability markup as a 2-tuple of strings"""
    specs, spellLikes = fullabilityparser.parseFullAbilities(fullTextStat)
    if specs is None:
        specs = ''
    else:
        specs = ''.join(specs)

    if spellLikes is None:
        spellLikes = ''

    return (specs, spellLikes)

def parseSpecialQualities(specialQualitiesStats):
    """All full ability markup as a list of strings"""
    return specialparser.parseSpecialQualities(specialQualitiesStats)

# tests
def test_statblockSkill():
    skillStats = query._allSkillStats()
    for s in skillStats:
        if s is None:
            continue

        try:
            parseSkills(s)
        except Exception, e:
            print s
            print e
            raise

def test_statblockFeat():
    featStats = query._allFeatStats()
    for f in featStats:
        if f is None:
            continue

        try:
            parseFeats(f)
        except Exception, e:
            print f
            print e
            raise

def test_hitPoints():
    hpStats = query._allHPStats()
    for hp in hpStats:
        if hp is None:
            continue

        try:
            parseHitPoints(hp)
        except Exception, e:
            print hp
            print e
            raise

def test_saves():
    saveStats = query._allSaveStats()
    for saves in saveStats:
        if saves is None:
            continue

        try:
            parseSaves(saves)
        except Exception, e:
            print saves
            print e
            raise

def test_statblock():
    monsters = query._allMonsters()
    for monster in monsters:
        try:
            Statblock(monster.id)
        except Exception, e:
            print monster
            print e
            import sys, pdb; pdb.post_mortem(sys.exc_info()[2])


# run the tests
if __name__ == '__main__': # {{{
    import time

    print 'testing parseSaves'
    t1 = time.time()
    test_saves()
    print time.time() - t1
    t1 = time.time()
    print 'testing parseHitPoints'
    test_hitPoints()
    print time.time() - t1
    t1 = time.time()
    print 'testing statblockSkill'
    test_statblockSkill()
    print time.time() - t1
    t1 = time.time()
    print 'testing statblockFeat'
    test_statblockFeat()
    print time.time() - t1
    t1 = time.time()
    print 'testing statblock'
    test_statblock()
    print time.time() - t1
    t1 = time.time()
# }}}
