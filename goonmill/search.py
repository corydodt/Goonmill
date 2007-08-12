"""PyLucene-based indexing and searching
"""
# vi:ft=python
import sys, os

import re

from PyLucene import (IndexWriter, StandardAnalyzer, Document, Field,
        MultiFieldQueryParser, IndexSearcher)

from twisted.web import microdom, domhelpers
from twisted.python import usage

from goonmill.util import RESOURCE

slashRx = re.compile(r'\\([n"])')

def repSlash(m):
    if m.group(1) == 'n':
        return '\n'
    return m.group(1)

def indexMonster(writer, monster):
    _ft = re.sub(slashRx, repSlash, monster.full_text)
    full = textFromHtml(_ft)

    doc = Document()
    name_ = Field("name_", monster.name,
                  Field.Store.YES, Field.Index.TOKENIZED)
    name_.setBoost(2.0)
    full_text = Field("full_text", full,
                  Field.Store.YES, Field.Index.TOKENIZED)
    doc.add(name_)
    print '.',
    sys.stdout.flush()
    doc.add(full_text)

    writer.addDocument(doc)


def textFromHtml(htmlText):
    d = microdom.parseString(htmlText, beExtremelyLenient=1)
    s = domhelpers.gatherTextNodes(d, joinWith=" ")
    ## print '\n'.join('| ' + l for l in s.splitlines())
    return s


identity = lambda x: x


ALWAYS_SKIP = object()


class Query(usage.Options):
    def parseArgs(self, *terms):
        self['terms'] = terms

    def postOptions(self):
        searcher = IndexSearcher(RESOURCE('lucene-data'))
        qp = MultiFieldQueryParser(['name', 'full_text'], StandardAnalyzer())
        qp.setDefaultOperator(MultiFieldQueryParser.Operator.AND)
        fuzzy = ['%s~' % (t,) for t in self['terms']]
        terms = ' '.join(fuzzy)
        query = qp.parse(terms, )
        hits = searcher.search(query)

        for i, doc in hits:
            print doc.name.stringValue(), '(%s)' % (hits.score(i),)
            if i == 10:
                break

        if len(hits)>10:
            print ". . . and %s more." % (len(hits) - 10,)


def buildIndex(monsters):
    dataDir = RESOURCE('lucene-data')
    if os.path.exists(dataDir):
        return
    writer = IndexWriter(dataDir, StandardAnalyzer(), True)
    for monster in monsters:
        indexMonster(writer, monster)

def run(argv=None):
    if argv is None:
        argv = sys.argv
    o = Query()
    try:
        o.parseOptions(argv[1:])
    except usage.UsageError, e:
        print str(o)
        print str(e)
        return 1

    return 0

if __name__ == '__main__': sys.exit(run())
