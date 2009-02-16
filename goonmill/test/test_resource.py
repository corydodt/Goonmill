"""
Test various functionality in resource
"""
import re
import unittest

from .. import resource

class ResourceTestCase(unittest.TestCase):
    def test_searched(self):
        """
        Make sure monster ids are returned correctly
        """
        def t(terms, *tests):
            results = resource.searched(terms)
            for res, test in zip(results, tests):
                name, id, teaserRx = test
                self.assertEqual(res[:2], (name, id))
                show = "%s != %s" % (res[2], teaserRx)
                self.failIfEqual(re.match(teaserRx, res[2]), None, show)

            self.assertEqual(len(results), len(tests))

        t(u'camel', (u'Camel', 92, '.*hump.*'))
        t(u'dragon', (u'Dragon Turtle', 329, '.*turtles speak Aquan.*'),
                (u'Gold Dragon, Wyrmling', 305, '.*Hit Dice: 8d.*'),
                (u'Gold Dragon, Very young', 306, '.*Hit Dice: 11.*'),
                (u'Gold Dragon, Young', 307, '.*Hit Dice: 14.*'),
                (u'Gold Dragon, Juvenile', 308, '.*Hit Dice: 17.*'),
                (u'Gold Dragon, Young adult', 309, '.*Hit Dice: 20.*'),
                (u'Gold Dragon, Adult', 310, '.*Hit Dice: 23.*'),
                (u'Gold Dragon, Mature adult', 311, '.*Hit Dice: 26.*'),
                (u'Gold Dragon, Old', 312, '.*Hit Dice: 29.*'),
                (u'Gold Dragon, Very old', 313, '.*Hit Dice: 32.*'),
                )

