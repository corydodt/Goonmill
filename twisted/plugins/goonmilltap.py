"""
Twistd plugin to run Goonmill.

Twisted 2.5 or later is required to use this.
"""

from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from nevow import appserver
from goonmill.resource import Root
from goonmill.query2 import db

class Options(usage.Options):
    optParameters = [['port', 'p', '6680', 'Port to run on'],
                     ]
    optFlags = [['dev', None, 'Enable development features such as /sandbox']]


class STFUSite(appserver.NevowSite):
    """Website with <80 column logging"""
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


class GoonmillService(internet.TCPServer):
    def startService(self, *a, **kw):
        # build the search index.  block on this, it has to happen before app
        # startup.
        from goonmill import search
        search.buildIndex(db.allMonsters())

        internet.TCPServer.startService(self, *a, **kw)


class GoonmillServerMaker(object):
    """
    Framework boilerplate class: This is used by twistd to get the service
    class.

    Basically exists to hold the IServiceMaker interface so twistd can find
    the right makeService method to call.
    """
    implements(IServiceMaker, IPlugin)
    tapname = "goonmill"
    description = "The Goonmill statblock generator"
    options = Options

    def makeService(self, options):
        """
        Construct the test daemon.
        """
        resource = Root()
        factory = STFUSite(resource)
        return GoonmillService(int(options['port']), factory)

# Now construct an object which *provides* the relevant interfaces

# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = GoonmillServerMaker()
