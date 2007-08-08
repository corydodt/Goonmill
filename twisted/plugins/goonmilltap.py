"""
Twistd plugin to run Goonmill.

Twisted 2.5 or later is required to use this.
"""

from zope.interface import implements

from twisted.python import usage, util, log
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import strports

from nevow import appserver
from goonmill.resource import Root, VhostFakeRoot

class Options(usage.Options):
    optParameters = [['port', 'p', '6680', 'Port to run on'],
                     ## ['privkey', 'k', DEFAULT_PEM, 
                     ##     'Private key file for starting the SSL server'],
                     ## ['certificate', 'k', DEFAULT_PEM, 
                     ##     'Certificate file for starting the SSL server'],
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
        resource = VhostFakeRoot(Root(dev=options['dev']))
        factory = STFUSite(resource)
        port = 'tcp:%s' % (options['port'],)
        ## port = 'ssl:%s:privateKey=%s:certKey=%s' % (options['port'],
        ##         options['privkey'], options['certificate'])
        return strports.service(port, factory)

# Now construct an object which *provides* the relevant interfaces

# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = GoonmillServerMaker()
