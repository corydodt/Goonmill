"""
Authentication, via the checker, and authorization, via the realm
"""

from zope.interface import implements
from twisted.cred.portal import IRealm
from twisted.cred.checkers import ICredentialsChecker, ANONYMOUS
from twisted.cred.credentials import IUsernamePassword

from nevow.inevow import IResource

from .resource import GuardedRoot

class CookieRealm(object):
    implements(IRealm)
    def __init__(self, userDatabase):
        self.userDatabase = userDatabase

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            if avatarId is ANONYMOUS:
                gr = GuardedRoot(None, self.userDatabase)
                return (IResource, gr, lambda *a: None)
            else:
                raise NotImplemented()


class UserDatabaseChecker(object):
    implements(ICredentialsChecker)
    credentialInterfaces = (IUsernamePassword,)
    def __init__(self, userDatabase):
        self.userDatabase = userDatabase

    def requestAvatarId(self, creds):
        import pdb; pdb.set_trace()
        pass # find out what interfaces creds has
