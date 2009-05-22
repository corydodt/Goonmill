#/usr/bin/env python
import sys, os
from urlparse import urlparse

from twisted.internet import reactor, task, defer
from twisted.web.client import HTTPPageGetter, _parse, HTTPClientFactory, PartialDownloadError
from twisted.web import error
from twisted.python import log, failure

import simplejson
import BeautifulSoup

failedCount = 0
MAXFAILS = 10

def logErrWithCount(f):
    r = log.err(f)
    global failedCount
    failedCount += 1
    if failedCount >= MAXFAILS:
        log.msg("** stopping - too many errors")
        if reactor.running:
            reactor.stop()
    return r


def parseContentType(s):
    parts = s.split(';', 1)
    if len(parts) == 2:
        charset = parts[1].split('=', 1)[1].strip()
        return {'mimeType': parts[0], 'charset': charset}
    else:
        return {'mimeType': parts[0]}


class UnicodeHTTPPageGetter(HTTPPageGetter):
    def handleResponse(self, response):
        if self.quietLoss:
            return
        if self.failed:
            self.factory.noPage(
                failure.Failure(
                    error.Error(
                        self.status, self.message, response)))
        if self.factory.method.upper() == 'HEAD':
            # Callback with empty string, since there is never a response
            # body for HEAD requests.
            self.factory.page(u'')
        elif self.length != None and self.length != 0:
            self.factory.noPage(failure.Failure(
                PartialDownloadError(self.status, self.message, response)))
        else:
            _ct = self.factory.response_headers.get('content-type', 'text/plain')
            assert len(_ct) == 1
            ct = _ct[0]
            uresponse = response.decode(parseContentType(ct).get('charset', 'utf-8'))
            self.factory.page(uresponse)
        # server might be stupid and not close connection. admittedly
        # the fact we do only one request per connection is also
        # stupid...
        self.transport.loseConnection()


def getPageU(url, contextFactory=None, *args, **kwargs):
    """Download a web page as a unicode object.

    Download a page. Return a deferred, which will callback with a
    page (as a string) or errback with a description of the error.

    See HTTPClientFactory to see what extra args can be passed.
    """
    scheme, host, port, path = _parse(url)
    factory = HTTPClientFactory(url, *args, **kwargs)
    factory.protocol = UnicodeHTTPPageGetter
    if scheme == 'https':
        from twisted.internet import ssl
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return factory.deferred


def getImageURL(url):
    """
    Scrape url (an html resource) and get the damn image url already
    """
    def gotPage(p):
        try:
            soup = BeautifulSoup.BeautifulSoup(p)
        except UnicodeDecodeError:
            raise # import pdb; pdb.set_trace()
        for a in soup.findAll('a'):
            href = a.get('href') or ''
            if 'commons/' in href: return href.encode('utf-8')
    return getPageU(url).addCallbacks(gotPage, logErrWithCount)


def downloadOne(_, url, monster):
    url = url.encode('utf-8')
    filename = urlparse(url)[2].split('/')[-1]
    outfile = monster + '/' + filename
    if os.path.exists(outfile):
        return defer.succeed(None)
    return getImageURL(url)


def dlPageWrapper(line, tabwriter):
    data = simplejson.loads(line)
    assert len(data) == 1
    monster = data.keys()[0].encode('utf-8')
    print monster, ' '.join(('[%s]' % e[0] for e in enumerate(data[monster])))
    try:
        os.makedirs(monster)
    except EnvironmentError:
        pass

    d = defer.succeed(None)
    for url in data[monster]:
        d = d.addCallback(downloadOne, url,
                monster).addCallback(tabwriter.addUrl, monster)
    return d


class TabWriter(object):
    def __init__(self, filename):
        self.f = open(filename, 'a')

    def addUrl(self, url, monster, status=''):
        if url is None:
            return
        self.f.write('%s\t%s\t%s\n' % (monster, url, status))


def run(argv=None):
    if argv is None:
        argv = sys.argv[:]

    infile = open(argv[1])
    tw = TabWriter(argv[2])

    work = (dlPageWrapper(line, tw) for line in infile) # .readlines()[:50])

    d = defer.Deferred()
    c = task.Cooperator()
    dl = []
    for x in range(15):
        dl.append( c.coiterate(work) )

    defer.DeferredList(dl).addBoth(lambda _: reactor.stop())

    reactor.run()
    return 0


if __name__ == '__main__': sys.exit(run())

