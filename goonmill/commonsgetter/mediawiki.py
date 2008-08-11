#/usr/bin/env python
import sys
import subprocess

from twisted.internet import reactor, task, defer
from twisted.web.client import getPage
from twisted.python import log

from goonmill.query2 import db

from BeautifulSoup import BeautifulStoneSoup
import simplejson

def gotResult(res, outfile, *args):
    soup = BeautifulStoneSoup(res)
    links = soup.findAll('link')[1:]
    outfile.write(simplejson.dumps({args[0]: [
        link.string for link in links]
    }) + '\n')
    print args[0]

failedCount = 0

def failedResult(f, *args):
    global failedCount
    failedCount = failedCount + 1
    log.msg("** Error for %s follows: ____" % (args,))
    log.err(f)
    # let lynx format this for us
    if f.value.args[2].startswith('<!DOCTYPE'):
        p = subprocess.Popen("lynx -dump -stdin", shell=True,
                stdin=subprocess.PIPE).stdin
        p.write(f.value.args[2])

SEARCH = 'http://api.wikiwix.com/opensearch.php?lang=en&format=rss&page=1&boolop=and&type=img&disp=commons&action=%s'

def getPageWrapper(url, outfile, *args):
    if failedCount <= 10:
        d = getPage(url % (args,)).addCallback(gotResult, outfile, *args)
        d.addErrback(failedResult, *args)
        return d
    else:
        return defer.succeed(None)


def monsters():
    seen = set()
    for m in db.allMonsters():
        # remove text after commas, since it usually designates something
        # boring like size
        name = m.name.split(',', 1)[0]
        if name not in seen:
            yield name
        seen.add(name)



def run(argv=None):
    if argv is None:
        argv = sys.argv[:]
    outfile = open(argv[1], 'w')
    work = (getPageWrapper(SEARCH, outfile, m) for m in monsters())
    d = defer.Deferred()
    c = task.Cooperator()
    dl = []
    for x in range(10):
        dl.append( c.coiterate(work) )

    defer.DeferredList(dl).addBoth(lambda _: reactor.stop())

    reactor.run()
    return 0


if __name__ == '__main__': sys.exit(run())

