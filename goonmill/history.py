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
        self.count = 1
        self.label = ''
        print self.monster.name, self.monster.hit_dice,
        _parsed = self.parseHitPoints()
        if _parsed is None:
            self.hitPoints = ['Special'] * self.count
        else:
            hp = []
            for n in range(self.count):
                hp.extend([d.sum() for d in dice.roll(_parsed)])
            self.hitPoints = hp

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

