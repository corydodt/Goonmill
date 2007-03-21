"""
Twistd plugin to run Goonmill.

Twisted 2.5 or later is required to use this.
"""

from zope.interface import implements

from twisted.python import usage, util
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import strports

from nevow import appserver
from goonmill.resource import Root

class Options(usage.Options):
    optParameters = [['port', 'p', '6680', 'Port to run on'],
                     ## ['privkey', 'k', DEFAULT_PEM, 
                     ##     'Private key file for starting the SSL server'],
                     ## ['certificate', 'k', DEFAULT_PEM, 
                     ##     'Certificate file for starting the SSL server'],
                     ]

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
        factory = appserver.NevowSite(resource)
        port = 'tcp:%s' % (options['port'],)
        ## port = 'ssl:%s:privateKey=%s:certKey=%s' % (options['port'],
        ##         options['privkey'], options['certificate'])
        return strports.service(port, factory)

# Now construct an object which *provides* the relevant interfaces

# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = GoonmillServerMaker()
