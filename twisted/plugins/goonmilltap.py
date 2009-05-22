"""
Twistd plugin to run Goonmill.

Twisted 2.5 or later is required to use this.
"""

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

class Options(usage.Options):
    optParameters = [['port', 'p', '6680', 'Port to run on'],
                     ]
    optFlags = [['dev', None, 'Enable development features such as /sandbox']]


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
        Construct the goonmill
        """
        if options['dev']:
            try:
                import wingdbstub
                wingdbstub
            except ImportError:
                pass
        from goonmill.webserver import WebServer, WebSite
        site = WebSite()
        ws = WebServer(int(options['port']), site)
        ws.site = site
        return ws

# Now construct an object which *provides* the relevant interfaces

# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = GoonmillServerMaker()
