"""
The boilerplate behind the resources.  Start services and shit like that.
"""
from twisted.application import internet
from twisted.python import log

from nevow import appserver

from .resource import Root

class WebSite(appserver.NevowSite):
    """Website with <80 column logging"""
    def __init__(self, *a, **kw):
        appserver.NevowSite.__init__(self, Root(), *a, **kw)

    def log(self, request):
        uri = request.uri

        if 'jsmodule' in uri:
            uris = uri.split('/')
            n = uris.index('jsmodule')
            uris[n-1] = uris[n-1][:3] + '...'
            uri = '/'.join(uris)

        if len(uri) > 38:
            uri = '...' + uri[-35:]

        code = request.code
        if code != 200:
            code = '!%s!' % (code, )

        log.msg('%s %s' % (code, uri), system='HTTP', )


class WebServer(internet.TCPServer):
    def startService(self, *a, **kw):
        from . import user, auth

        r = self.site.resource
        userdb = user.userDatabase()
        # r.userDatabase = userdb
        r.realm = auth.CookieRealm(userdb)
        r.checkers = (auth.UserDatabaseChecker(userdb),)

        internet.TCPServer.startService(self, *a, **kw)


