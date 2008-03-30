"""
Users and user acquisition
"""
import hashlib

from storm import locals

from zope.interface import implements
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred import error, checkers, credentials
from twisted.cred.portal import Portal, IRealm
from twisted.internet import defer

from goonmill.util import RESOURCE


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
    # may not need:
    # workspace = locals.Reference(workspaceId, Workspace.id)

    # store a (pickle?) here of the object that is the
    # constituent.
    # use adapters later to produce das Ding an Sich
    data = locals.RawStr()

    # here we probably eventually need a search-findable form of
    # the data

    # here we probably also need some other tidbits needed to
    # display it.  for monster group, a count?  for any, an image?

Workspace.constituents = locals.ReferenceSet(
        Workspace.id,
        Constituent.workspaceId,
        Constituent.id)


class UserDatabase(object):
    """A user database"""
    def __init__(self):
        self.db = locals.create_database('sqlite:///' + RESOURCE('user.db'))
        self.store = locals.Store(self.db)

