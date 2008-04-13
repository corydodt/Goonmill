"""
Users and user acquisition
"""
from storm import locals

from .util import RESOURCE

from zope.interface import Interface, implements, Attribute
from twisted.python.components import registerAdapter


KIND_MONSTERGROUP = u'monsterGroup'
KIND_NPC = u'npc'
KIND_STENCIL = u'stencil'
KIND_ENCOUNTER = u'encounter'

class User(object):
    """A User"""
    __storm_table__ = 'user'
    id = locals.Int(primary=True)                #
    name = locals.Unicode()
    passwordHash = locals.Unicode()
    cookie = locals.Unicode()


# class Library: ? - no, there's only one library per user.  Just
# associate items directly to a user.

class Workspace(object):
    """
    """
    __storm_table__ = 'workspace'
    id = locals.Int(primary=True)
    name = locals.Unicode()

    userId = locals.Int()
    # may not need:
    # user = locals.Reference(userId, User.id)

    url = locals.Unicode()

User.workspaces = locals.ReferenceSet(
        User.id,
        Workspace.userId,
)


class IRealConstituent(Interface):
    """
    The inner monster or encounter or whatever of a constituent
    """


# Major FIXME - when an NPC or Stencil is found on more than one workspace,
# it should be a singleton.  As currently designed, all constituents are
# separate by workspace, meaning there are differing clones of NPC everywhere.
# Possible solution: make a glue table between workspace and constituent

class Constituent(object):
    """
    An item that can be found in a workspace, i.e. monster group,
    npc, encounter, or stencil
    """
    implements(IRealConstituent)

    __storm_table__ = 'constituent'
    id = locals.Int(primary=True)
    name = locals.Unicode() # Alias, or personal name, not monster name
    base = locals.Int() # Id of some base monster; None for encounter/stencil
    otherId = locals.Int() # Reference to some other table (monsterGroup, npc, stencil, encounter) resolved by the adapter
    kind = locals.Unicode() # is monsterGroup, npc, encounter or stencil
    userId = locals.Int() # the user owning this
    workspaceId = locals.Int() # the workspace this is found on
    workspace = locals.Reference(workspaceId, Workspace.id)
    # we need a search-findable form of the data as an attribute (?)
    # image = locals.Unicode()

    @classmethod
    def monsterGroupKind(cls, monster, count, workspace):
        """
        Return a Constituent instance that is configured as a monsterGroup
        (c.kind=monsterGroup and c.data is a json-ized
        goonmill.user.MonsterGroup)
        """
        c = cls()
        c.kind = KIND_MONSTERGROUP
        c.name = u''
        c.base = monster.id
        c.workspace = workspace
        c.userId = workspace.userId

        mg = MonsterGroup()
        c.otherId = mg.id
        theStore.add(mg)
        
        assert count < 123

        for n in range(count):
            groupie = Groupie()
            groupie.monsterGroup = mg
            theStore.add(groupie)

        theStore.add(c)
        theStore.commit()
        return c

    @classmethod
    def npcKind(cls, monster, workspace):
        c = cls()
        c.kind = KIND_NPC
        c.name = u'Nameless NPC %s' % (monster.name.capitalize(),)
        c.base = monster.id
        c.workspace = workspace
        c.userId = workspace.userId
        
        npc = NPC()
        c.otherId = npc.id
        theStore.add(npc)

        theStore.add(c)
        theStore.commit()
        return c

    def isLibraryKind(self):
        """
        Is this the kind of constituent that can appear in the user's
        permanent library?
        """
        return self.kind not in [KIND_MONSTERGROUP, KIND_ENCOUNTER]

    def briefDetail(self):
        """
        The text for brief details about the creature (i.e. count or NPC
        stats)
        """
        return self.fuckComponentArchitecture().briefDetail()

    def fuckComponentArchitecture(self):
        """
        Return the inner monster
        """
        kind = self.kind
        if kind == KIND_MONSTERGROUP:
            return theStore.get(MonsterGroup, self.otherId)
        elif kind == KIND_NPC:
            return theStore.get(NPC, self.otherId)
        elif kind == KIND_STENCIL:
            return theStore.get(Stencil, self.otherId)
        elif kind == KIND_ENCOUNTER:
            return theStore.get(Encounter, self.otherId)

    def getStencilBase(self):
        """
        Return the base creature for the stencil
        """
        from .query2 import db
        if (self.base < 1000):
            ret = db.lookup(self.base)
        else: 
            ret = theStore.get(Stencil, self.base)
        return ret

Workspace.constituents = locals.ReferenceSet(
        Workspace.id,
        Constituent.workspaceId,
)


class MonsterGroup(object):
    """
    A group of monsters of the same kind
    """
    __storm_table__ = 'monsterGroup'
    id = locals.Int(primary=True)

    def briefDetail(self):
        return str(len(list(self.groupies)))


class Stencil(object):
    """
    A monster stencil, used as the base for other monsters
    """
    __storm_table__ = 'stencil'
    id = locals.Int(primary=True)

    def briefDetail(self):
        return u''


class Encounter(object):
    """
    A group of monsters of the same kind
    """
    __storm_table__ = 'encounter'
    id = locals.Int(primary=True)

    def briefDetail(self):
        return u''


class Groupie(object):
    """
    A single monster in a monster group
    """
    __storm_table__ = 'groupie'
    id = locals.Int(primary=True)
    monsterGroupId = locals.Int()
    monsterGroup = locals.Reference(monsterGroupId, MonsterGroup.id)
    gear = locals.Unicode()
    spells = locals.Unicode()


MonsterGroup.groupies = locals.ReferenceSet(
        MonsterGroup.id,
        Groupie.monsterGroupId,
)


class NPC(object):
    """
    One of those NPC guys
    """
    __storm_table__ = 'npc'
    id = locals.Int(primary=True)
    classes = locals.Unicode()
    gear = locals.Unicode()
    spells = locals.Unicode()

    def briefDetail(self):
        return self.classes


# the global store object. yay, global mutable state!
theStore = None


def userDatabase():
    """Give a user database"""
    import goonmill.user as this
    global theStore
    if theStore is not None:
        raise RuntimeError("Already created a db store")
    db = locals.create_database('sqlite:///' + RESOURCE('user.db'))
    theStore = locals.Store(db)
    return theStore

