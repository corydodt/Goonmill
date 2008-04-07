"""
Users and user acquisition
"""
from storm import locals

from .util import RESOURCE


class User(object):
    """A User"""
    __storm_table__ = 'user'
    id = locals.Int(primary=True)                #
    name = locals.Unicode()
    password = locals.Unicode()
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
        Workspace.id)


class Constituent(object):
    """
    An item that can be found in a workspace, i.e. monster group,
    npc, encounter, or stencil
    """
    __storm_table__ = 'constituent'
    id = locals.Int(primary=True)
    name = locals.Unicode()

    # kind is u'monster group', u'npc', u'encounter', or
    # u'stencil'
    kind = locals.Unicode()

    userId = locals.Int()

    workspaceId = locals.Int()
    workspace = locals.Reference(workspaceId, Workspace.id)

    # store a (pickle?) here of the object that is the
    # constituent.
    # use adapters later to produce das Ding an Sich
    data = locals.RawStr()

    # here we probably eventually need a search-findable form of
    # the data

    # here we probably also need some other tidbits needed to
    # display it.  for monster group, a count?  for any, an image?


    @classmethod
    def monsterGroupFromMonster(cls, monster, workspace):
        c = cls()
        c.name = monster.name
        c.workspace = workspace
        c.userId = workspace.userId
        c.data = 'DUMMY DATA TODO'
        c.kind = u'monsterGroup'
        theStore.add(c)
        theStore.commit()
        return c

    @classmethod
    def npcFromMonster(cls, monster, workspace):
        c = cls()
        c.name = u'Nameless NPC %s' % (monster.name.capitalize(),)
        c.workspace = workspace
        c.userId = workspace.userId
        c.data = str(monster.name + ':DUMMY DATA TODO')
        c.kind = u'npc'
        theStore.add(c)
        theStore.commit()
        return c

    def isLibraryKind(self):
        """
        Is this the kind of constituent that can appear in the user's
        permanent library?
        """
        return self.kind not in ['monsterGroup', 'encounter']

    def briefDetail(self):
        """
        The text for brief details about the creature (i.e. count or NPC
        stats)
        """
        if self.kind == 'monsterGroup':
            return u'n'
        elif self.kind == 'npc':
            return u'clsN / clsM / ...'
        return u''

Workspace.constituents = locals.ReferenceSet(
        Workspace.id,
        Constituent.workspaceId,
        Constituent.id)

# the global store object. yay, global mutable state!
theStore = None


def userDatabase():
    """Give a user database"""
    import goonmill.user as this
    if theStore is not None:
        raise RuntimeError("Already created a db store")
    db = locals.create_database('sqlite:///' + RESOURCE('user.db'))
    global theStore
    theStore = locals.Store(db)
    return theStore

