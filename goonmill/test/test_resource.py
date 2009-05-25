"""
Test various functionality in resource
"""
import re

from storm.locals import Store

from twisted.trial import unittest
from twisted.internet import defer

import fudge

from .. import resource, user

class ResourceTestCase(unittest.TestCase):
    def test_searched(self):
        """
        Make sure monster ids are returned correctly
        """
        def t(terms, *tests):
            results = resource.searched(terms)
            self.assertEqual(len(results), len(tests))

            for res, test in zip(results, tests):
                name, id, teaserRx = test
                self.assertEqual(res[:2], (name, id))
                show = "%s != %s" % (res[2], teaserRx)
                self.failIfEqual(re.match(teaserRx, res[2]), None, show)

        t(u'camel', (u'Camel', 92, '.*hump.*'))
        t(u'dragon', 
                (u'Dragon Turtle',                 329,   '.*turtles speak Aquan.*'),
                (u'Gold Dragon, Wyrmling',         305,   '.*Hit Dice: 8d.*'),
                (u'Black Dragon, Wyrmling',        209,   '.*Hit Dice: 4.*'),
                (u'Black Dragon, Very young',      210,   '.*Very.*Hit Dice: 7.*'),
                (u'Black Dragon, Young',           211,   '.*Young.*Hit Dice: 1.*'),
                (u'Black Dragon, Juvenile',        212,   '.*Juvenile.*Hit Dice: 1.*'),
                (u'Gold Dragon, Very young',       306,   '.*Hit Dice: 11.*'),
                (u'Gold Dragon, Young',            307,   '.*Hit Dice: 14.*'),
                (u'Gold Dragon, Juvenile',         308,   '.*Hit Dice: 17.*'),
                (u'Gold Dragon, Young adult',      309,   '.*Hit Dice: 20.*'),
                )


class BasicSearchTest(unittest.TestCase):
    def setUp(self):
        workspace = user.Workspace()
        self.bs = resource.BasicSearch(workspace)
        fragmentParent = fudge.Fake("WorkspacePage")
        fragmentParent.provides("page")
        fragmentParent.liveFragmentChildren = []
        cl = fragmentParent.constituentList = resource.ConstituentList(workspace)
        d = defer.succeed(None)
        cl.page = fudge.Fake("Page").provides("callRemote").returns(d)
        cl._athenaID = fudge.Fake("_athenaID")
        fragmentParent.eventBus = resource.EventBus()
        self.bs.setFragmentParent(fragmentParent)
        self.store = user.userDatabase('sqlite:')

    def test_newMonsterGroup(self):
        """
        We can get a monster by calling newMonsterGroup
        """
        mohrg = 501
        count = 2
        d = self.bs.newMonsterGroup(mohrg, count)
        def check(mgv):
            con = mgv.constituent
            m = con.fuckComponentArchitecture()
            self.assertEqual(m.stencilId, 501)
            self.assertEqual(m.id, 1)
            store = Store.of(con)
            count = store.find(user.Groupie, user.Groupie.constituent ==
                    con).count()
            self.assertEqual(count, 2)
        d.addCallback(check)
        return d

