#/usr/bin/env python
import sys, os
from urlparse import urlparse

import tempfile

from twisted.internet import reactor, task, defer
from twisted.web.client import downloadPage
from twisted.python import log

failedCount = 0

MAXFAILS = 15


def logErrWithCount(f, outfile):
    r = log.err(f)
    log.msg("** failed: %s" % (outfile,))
    global failedCount
    failedCount += 1
    if failedCount >= MAXFAILS:
        log.msg("** stopping - too many errors")
        if reactor.running:
            reactor.stop()
    return r


def downloadOne(url, monster):
    filename = urlparse(url)[2].split('/')[-1]
    outfile = monster + '/' + filename
    if os.path.exists(outfile):
        return defer.succeed(None)
    return downloadPage(url, outfile).addErrback(logErrWithCount, outfile)


def dlPageWrapper(linetracker, monster, url, status):
    if status == 'ok':
        return defer.succeed(None)

    print monster

    try:
        os.makedirs(monster)
    except EnvironmentError:
        pass

    def updateLineTracker(_, monster, url, status):
        linetracker.add(monster, url, status)

    d = downloadOne(url, monster)
    d.addCallback(updateLineTracker, monster, url, 'ok')
    d.addErrback(updateLineTracker, monster, url, 'failed')
    return d


class LineTracker(object):
    def __init__(self, infile):
        self.f = open(infile, 'r')
        self.lines = []

    def __iter__(self):
        return (line.strip('\n').split('\t') for line in self.f)

    def add(self, monster, filename, status):
        self.lines.append((monster, filename, status))

    def dump(self, filename):
        out = open(filename, 'w')
        for line in self.lines:
            out.write('\t'.join(line) + '\n')

    def flush(self):
        """process all remaining lines immediately"""
        for line in self:
            self.add(*line)

    def finalize(self):
        """
        Save back to disk for quitting
        """
        self.flush()
        self.replaceAtomically()

    def replaceAtomically(self):
        """
        Save over self.f, atomic via rename
        """
        fname = self.f.name

        self.f.close()
        try:
            tmp = tempfile.mktemp()
            self.dump(tmp)
            os.rename(tmp, fname)
        finally:
            self.__init__(fname)


def run(argv=None):
    if argv is None:
        argv = sys.argv[:]

    lt = LineTracker(sys.argv[1])
    try:
        work = (dlPageWrapper(lt, *line) for line in lt)

        c = task.Cooperator()
        dl = []
        for x in range(15):
            dl.append( c.coiterate(work) )

        defer.DeferredList(dl).addBoth(lambda _: reactor.stop())

        reactor.run()
    finally:
        lt.finalize()
    return 0


if __name__ == '__main__': sys.exit(run())

