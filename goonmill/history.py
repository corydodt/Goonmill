"""The history of statblocks for this session"""

import re

import pyparsing

from goonmill import query, dice, diceparser, skillparser, featparser

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
        self.overrides = {
                'count': self._count,
                'label': self._label,
                'acFeats': lambda: self.formatFeats(self.acFeats),
                'speedFeats': lambda: self.formatFeats(self.speedFeats),
                'specialActionFeats': lambda: self.formatFeats(self.specialActionFeats),
                'attackOptionFeats': lambda: self.formatFeats(self.attackOptionFeats),
                'rangedAttackFeats': lambda: self.formatFeats(self.rangedAttackFeats),
                }
        self.feats = self.parseFeats()
        self.skills = self.parseSkills()
        self._handler = None

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

    def parseFeats(self):
        return parseFeats(self.monster.feats)

    def parseSkills(self):
        return parseSkills(self.monster.skills)

    def formatFeats(self, callable):
        featList = callable()
        return ', '.join([f.name for f in featList])

    def acFeats(self):
        return [f for f in self.feats if f.is_ac_feat]

    def speedFeats(self):
        return [f for f in self.feats if f.is_speed_feat]

    def specialActionFeats(self):
        return [f for f in self.feats if f.is_special_action_feat]

    def attackOptionFeats(self):
        return [f for f in self.feats if f.is_attack_option_feat]

    def rangedAttackFeats(self):
        return [f for f in self.feats if f.is_ranged_attack_feat]

    def hitPoints(self):
        """
        @return: A sequence of hit points
        """
        _parsed = self.parseHitPoints()
        hplist = []
        if _parsed is None:
            hplist = ['Special'] * self._count
        else:
            for n in range(self._count):
                rolled = list(dice.roll(_parsed))
                assert len(rolled) == 1, "Too many repeats in this expression - a monter may have only one hit dice expression with no repeats!"
                hplist.append(rolled[0].sum())

            # minimum of 1hp for a monster
            for n, hp in enumerate(hplist):
                if hp < 1: 
                    hplist[n] = 1

        return ', '.join(map(str, hplist))

    def parseHitPoints(self):
        """Roll hit points for one monster of this type"""
        m = hpParser.match(self.monster.hit_dice)
        if m is None:
            # monster has very non-standard hit dice (e.g. Psicrystal)
            return 

        p = diceparser.dice_string.parseString
        # try parsing the first group as a dice expression. if that fails,
        # return the second group as non-random hit points.
        try:
            _parsed = p(m.group(1))
            return _parsed
        except pyparsing.ParseException:
            return p(m.group(2))

    def get(self, attribute):
        """
        Retrieve an attribute, first by looking it up in my own property list
        (which might have been modified from the server) and second by looking
        it up in the monster's ORM object.
        """
        if attribute in self.overrides:
            att = self.overrides[attribute]
            if callable(att):
                return att()
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


class StatblockSkill(object):
    """A skill owned by a monster"""
    def __init__(self, id, value, subSkill=None, splat=None, qualifier=None):
        self.splat = splat
        self.value = value
        self.skill = query.lookupSkill(id)
        ## assert self.skill is not None
        self.subSkill = subSkill
        self.qualifier = qualifier

    def __repr__(self):
        sub = ''
        if self.subSkill is not None:
            sub = ' (%s)' % (self.subSkill,)

        qual = ''
        if self.qualifier is not None:
            qual = ' (%s)' % (self.qualifier,)

        splat = ''
        if self.splat is not None:
            splat = '*'

        if self.value:
            return "<%s%s %+g%s%s>" % (self.skill.name, sub, self.value, splat, qual)
        else:
            return "<%s%s %s%s>" % (self.skill.name, sub, splat, qual)


def parseFeats(featStat):
    ret = []
    # check this before trying to parse
    if featStat is None:
        return ret

    parsed = featparser.featStat.parseString(featStat)

    if parsed.emptyList:
        return ret

    for entry in parsed:
        if entry.lycanthrope:
            base = entry.lycanthrope
        else:
            base = entry.featName

        subs = entry.subFeatGroup
        if subs:
            for sub in subs:
                ret.append(StatblockFeat(base, sub))
        else:
            ret.append(StatblockFeat(base))

    return ret


def parseSkills(skillStat):
    ret = []

    # check this before trying to parse
    if skillStat is None:
        return ret

    parsed = skillparser.skillStat.parseString(skillStat)

    if parsed.emptyList:
        return ret

    for entry in parsed:
        if entry.skillName: 
            base = entry.skillName
            val = entry.number
        else:
            ## this is a language - TODO set a language flag
            base = entry.languageName
            val = None
        qualifier = entry.qualifier
        subs = entry.subSkillGroup
        splat = entry.splat
        if subs:
            for sub in subs:
                ret.append(StatblockSkill(base, val, sub, splat or None, qualifier or None))
        else:
            ret.append(StatblockSkill(base, val, splat=(splat or None),
                qualifier=(qualifier or None)))

    return ret


class StatblockFeat(object):
    """A feat owned by a monster"""
    def __init__(self, id, qualifier=None):
        self.feat = query.lookupFeat(id)
        ## assert self.feat is not None
        self.qualifier = qualifier

    def __repr__(self):
        q = ""
        if self.qualifier:
            q = " (%s)" % (self.qualifier,)
        return "<StatblockFeat %s%s>" % (self.feat.name, q)


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

def test_statblock():
    monsters = query._allMonsters()
    for monster in monsters:
        try:
            Statblock(monster.id)
        except Exception, e:
            print monster
            print e
            import sys, pdb; pdb.post_mortem(sys.exc_info()[2])

if __name__ == '__main__': # {{{
    print 'testing statblockSkill'
    test_statblockSkill()
    print 'testing statblockFeat'
    test_statblockFeat()
    print 'testing statblock'
    test_statblock()
# }}}
