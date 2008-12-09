"""HyperEstraier-based indexing and searching """
# vi:ft=python
import sys, os
import shutil
import re

from twisted.web import microdom, domhelpers
from twisted.python import usage

import hypy

from goonmill.util import RESOURCE


INDEX_DIRECTORY = RESOURCE('search-index')

slashRx = re.compile(r'\\([n"])')

def repSlash(m):
    if m.group(1) == 'n':
        return '\n'
    return m.group(1)

def indexMonster(database, monster):
    _ft = re.sub(slashRx, repSlash, monster.full_text)
    full = textFromHtml(_ft)
    doc = hypy.HDocument(uri=unicode(monster.id))
    doc.addText(full)
    doc[u'@name'] = monster.name
    # add monster.name to the text so that it has extra weight in the
    # search results
    doc.addHiddenText(monster.name)

    database.putDoc(doc, 0)

    sys.stdout.write(".")
    sys.stdout.flush()


def textFromHtml(htmlText):
    d = microdom.parseString(htmlText, beExtremelyLenient=1)
    s = domhelpers.gatherTextNodes(d, joinWith=" ")
    ## print '\n'.join('| ' + l for l in s.splitlines())
    return s


identity = lambda x: x


ALWAYS_SKIP = object()

def fuzzyQuoteTerm(t):
    """Return a string term, quoted if a phrase, and with the fuzzy operator"""
    if ' ' in t:
        return t
    return '%s*' % (t,)


def find(terms):
    """Use the estraier index to find monsters"""
    fuzzy = [fuzzyQuoteTerm(t) for t in terms]
    phrase = ' '.join(fuzzy)
    estdb = hypy.HDatabase()
    estdb.open(INDEX_DIRECTORY, 'r')

    query = hypy.HCondition(phrase, matching='simple', max=10)

    return estdb.search(query)


def buildIndex(monsters):
    if os.path.exists(INDEX_DIRECTORY):
        return
    estdb = hypy.HDatabase()
    estdb.open(INDEX_DIRECTORY, 'a')

    for n, monster in enumerate(monsters):
        if n%100 == 0:
            sys.stdout.write("%s" % (n,))
        indexMonster(estdb, monster)

    estdb.close()


class Options(usage.Options):
    optFlags = [
            ['build-index', 'b', 'Build a fresh index']

            ]

    def parseArgs(self, *terms):
        self['terms'] = terms

    def postOptions(self):
        if self['build-index']:
            try:
                shutil.rmtree(INDEX_DIRECTORY)
            except EnvironmentError, e:
                pass

            from goonmill.query2 import db
            buildIndex(db.allMonsters())

        else:
            # try: FIXME
            for hit in find(self['terms']):
                # print hit.name, hit.score
                print hit['@name']
            # except lucene.JavaError, e: FIXME - need the hypy version of
            # this code
            #   if 'FileNotFoundException' in str(e):
            #       raise usage.UsageError(
            #               "** Missing index directory.  Run with --build-index")




def run(argv=None):
    if argv is None:
        argv = sys.argv
    o = Options()
    try:
        o.parseOptions(argv[1:])
    except usage.UsageError, e:
        print str(o)
        print str(e)
        return 1

    return 0

if __name__ == '__main__': sys.exit(run())

