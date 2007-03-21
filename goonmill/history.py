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
        self.pendingStatblocks = []

    def setView(self, view):
        """
        Set the output result element, which will be notified when I change.
        """
        self.view = view

    def addStatblock(self, statblock):
        ## TODO - limit the number of statblocks i can hold to some reasonable
        ## number to prevent DoS
        self.statblocks.append(statblock)
        self.pendingStatblocks.append(statblock)
        self.view.historyUpdated(self)

    def pendingStatblocks(self):
        return self.pendingStatblocks

    def unpendStatblocks(self, statblocks):
        for block in statblocks:
            if block in self.pendingStatblocks:
                del self.pendingStatblocks[block]

miniParser = re.compile(r'(\S+)\s[^(]*\(([\d,]+) hp\)')

class Statblock(object):
    """
    A representation of one statblock; a configured monster that has had
    its hit points generated and labels set up.
    """
    def __init__(self, id, count, label):
        self.monster = query.lookup(id)
        self.count = count
        self.label = label
        print self.monster.name, self.monster.hit_dice,
        _parsed = self.parseHitPoints()
        if _parsed is None:
            self.hitPoints = ['Special'] * count
        else:
            self.hitPoints = [d.sum() for d in dice.roll(_parsed)]

        for n, hp in enumerate(self.hitPoints):
            if hp < 1: 
                self.hitPoints[n] = 1

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

