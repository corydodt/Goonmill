"""The history of statblocks for this session"""

import re

import pyparsing

from goonmill import query, dice, diceparser

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

miniParser = re.compile(r'(\S+)\s[^(]*\(([\d,]+) hp\)')

class Statblock(object):
    """
    A representation of one statblock; a configured monster that has had
    its hit points generated and labels set up.
    """
    def __init__(self, id):
        self.monster = query.lookup(id)
        self._count = 1
        self._label = ''
        self.overridden = {
                'count': self._count,
                'label': self._label,
                }

    def hitPoints(self):
        """
        @return: A sequence of hit points
        """
        _parsed = self.parseHitPoints()
        hplist = []
        if _parsed is None:
            return ['Special'] * self._count
        else:
            for n in range(self._count):
                rolled = list(dice.roll(_parsed))
                assert len(rolled) == 1, "Too many repeats in this expression - a monter may have only one hit dice expression with no repeats!"
                hplist.append(rolled[0].sum())

        for n, hp in enumerate(hplist):
            if hp < 1: 
                hplist[n] = 1

        return hplist

    def parseHitPoints(self):
        """Roll hit points for one monster of this type"""
        m = miniParser.match(self.monster.hit_dice)
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
        if attribute in self.overridden:
            return self.overridden[attribute]
        return getattr(self.monster, attribute)
