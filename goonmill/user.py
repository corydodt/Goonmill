"""
Users and user acquisition
"""
from storm import locals

from .util import RESOURCE
from .history import Statblock

from zope.interface import Interface, implements

KIND_NPC = u'npc'
KIND_MONSTERGROUP = u'monsterGroup'
KIND_ENCOUNTER = u'encounter'
TOO_MANY_GROUPIES = 123

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


# Major FIXME - when an NPC or Stencil is found on more than one workspace,
# it should be a singleton.  As currently designed, all constituents are
# separate by workspace, meaning there are differing clones of NPC everywhere.
# Possible solution: make a glue table between workspace and constituent

class Constituent(object):
    """
    An item that can be found in a workspace, i.e. monster group,
    npc, encounter, or stencil
    """
    __storm_table__ = 'workspaceConstituent'
    id = locals.Int(primary=True)
    workspaceId = locals.Int() # the workspace this is found on
    workspace = locals.Reference(workspaceId, Workspace.id)
    npcId = locals.Int()
    monsterGroupId = locals.Int()
    encounterId = locals.Int()

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
        c.name = u''
        c.workspace = workspace

        mg = MonsterGroup()
        mg.stencilId = monster.id
        theStore.add(mg)
        mg.id = locals.AutoReload
        c.monsterGroupId = mg.id
        
        assert count < TOO_MANY_GROUPIES

        for n in range(count):
            groupie = Groupie()
            groupie.monsterGroup = mg
            theStore.add(groupie)

        theStore.add(c)
        theStore.commit()

        assert c.fuckComponentArchitecture() is mg
        assert c.fuckComponentArchitecture().stencilId == monster.id

        return c

    @classmethod
    def npcKind(cls, monster, workspace):
        c = cls()
        c.name = u'Nameless NPC %s' % (monster.name.capitalize(),)
        c.stencilId = monster.id
        c.workspace = workspace
        
        npc = NPC()
        npc.id = locals.AutoReload
        c.npcId = npc.id
        theStore.add(npc)

        theStore.add(c)
        theStore.commit()
        return c

    def isLibraryKind(self):
        """
        Is this the kind of constituent that can appear in the user's
        permanent library?
        """
        return not (self.encounterId or self.monsterGroupId)

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
        if self.monsterGroupId:
            return theStore.get(MonsterGroup, self.monsterGroupId)
        elif self.npcId:
            return theStore.get(NPC, self.npcId)
        elif self.encounterId:
            return theStore.get(Encounter, self.encounterId)

    def getStencilBase(self):
        """
        Return the base creature for the stencil
        """
        if self.npcId or self.monsterGroupId:
            o = self.fuckComponentArchitecture()
            return getStencil(o.stencilId)
        return None

    def kind(self):
        """
        Which kind of constituent is this? as string name
        """
        if self.npcId:
            return KIND_NPC
        elif self.monsterGroupId:
            return KIND_MONSTERGROUP
        elif self.encounterId:
            return KIND_ENCOUNTER
        assert 0, "Could not identify this kind of monsterGroup"


    def __repr__(self):
        inner = self.fuckComponentArchitecture()
        return '<Constituent|%s %r at 0x%x>' % (self.id, inner, id(self))


def getStencil(id):
    from .query2 import db
    return db.lookup(id)


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
    stencilId = locals.Int()
    name = locals.Unicode()

    def briefDetail(self):
        return unicode(len(list(self.groupies)))

    def __repr__(self):
        base = getStencil(self.stencilId).name
        return '<MonsterGroup|%s of %s at 0x%x>' % (self.id, base, id(self))


class Encounter(object):
    """
    A group of monsters of the same kind
    """
    __storm_table__ = 'encounter'
    id = locals.Int(primary=True)
    name = locals.Unicode()

    def briefDetail(self):
        return u''

    def __repr__(self):
        return '<Encounter|%s at 0x%x>' % (self.id, id(self))


class Groupie(object):
    """
    A single monster in a monster group
    """
    __storm_table__ = 'groupie'
    id = locals.Int(primary=True)
    monsterGroupId = locals.Int()
    monsterGroup = locals.Reference(monsterGroupId, MonsterGroup.id)
    constituent = locals.Reference(monsterGroupId, Constituent.monsterGroupId)
    hitPoints = locals.Int()
    alignment = locals.Unicode()
    name = locals.Unicode()
    gear = locals.Unicode()
    spells = locals.Unicode()

    def randomize(self, overwrite=True):
        """
        Generate random dierolled attributes.  Currently this means hit points
        and alignment.

        If overwrite=False, do not overwrite any attributes that are already
        set.
        """
        base = self.constituent.getStencilBase()
        sb = Statblock.fromMonster(base)
        if overwrite == True or self.hitPoints is None:
            self.hitPoints = sb.singleHitPoints()
        if overwrite == True or self.alignment is None:
            self.alignment = sb.formatAlignment()


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
    name = locals.Unicode()
    stencilId = locals.Int()
    classes = locals.Unicode()
    gear = locals.Unicode()
    spells = locals.Unicode()

    def briefDetail(self):
        return self.classes

    def __repr__(self):
        base = getStencil(self.stencilId).name
        return '<NPC|%s of %s at 0x%x>' % (self.id, base, id(self))


# the global store object. yay, global mutable state!
theStore = None


def userDatabase():
    """Give a user database"""
    global theStore
    if theStore is not None:
        raise RuntimeError("Already created a db store")
    db = locals.create_database('sqlite:///' + RESOURCE('user.db'))
    theStore = locals.Store(db)
    return theStore

