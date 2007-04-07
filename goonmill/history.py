"""The history of statblocks for this session"""

import re

import pyparsing

from goonmill import query, dice, diceparser, skillparser

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
        ret = []
        if self.monster.feats in ['-', None]:
            return []

        parsed = [f.strip() for f in self.monster.feats.split(',')]

        for feat in parsed:
            ffeat = query.lookupFeat(feat)
            ret.append(ffeat)

        return ret

    def parseSkills(self):
        ret = []
        parsed = skillparser.skillStat.parseString(self.monster.skills)

        if parsed.noSkillList:
            return ret

        for entry in parsed:
            if entry.skillName: 
                ## this is a language
                base = entry.skillName
                val = entry.number
            else:
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

    def acFeats(self):
        return [f for f in self.feats if f.is_ac_feat]

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
            return self.overrides[attribute]
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


class StatblockFeat(object):
    """A feat owned by a monster"""
    def __init__(self, id):
        self.feat = query.lookupFeat(id)

def test_statblockSkill():
    skillStats = query._allSkillStats()
    for s in skillStats:
        if s is None:
            continue

        try:
            skillparser.skillStat.parseString(s)
        except Exception, e:
            print s
            raise


def test_statblock():
    monsters = query._allMonsters()
    for monster in monsters:
        try:
            Statblock(monster.id)
        except Exception, e:
            print monster
            import sys, pdb; pdb.post_mortem(sys.exc_info()[2])

if __name__ == '__main__': # {{{
    print 'testing statblockSkill'
    ## test_statblockSkill()
    print 'testing statblock'
    test_statblock()
# }}}
