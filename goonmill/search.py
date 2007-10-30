"""PyLucene-based indexing and searching
"""
# vi:ft=python
import sys, os

import re

try:
    from PyLucene import (IndexWriter, StandardAnalyzer, Document, Field,
            MultiFieldQueryParser, IndexSearcher)
except ImportError:
    from lucene import (IndexWriter, StandardAnalyzer, Document, Field,
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
    id = Field("id", str(monster.id),
                  Field.Store.YES, Field.Index.UN_TOKENIZED)
    doc.add(name_)
    doc.add(full_text)
    doc.add(id)

    writer.addDocument(doc)
    print '.',
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
        return '"%s"~' % (t,)
    return '%s~' % (t,)


class Hit(object):
    """One monster search result
    Essentially an adapter for Lucene's hits
    """
    def __init__(self, doc, hits, index):
        self.name = doc['name_']
        self.id = doc['id']
        self.score = hits.score(index)

    def __repr__(self):
        return "<Hit name=%s %s%%>" % (self.name, int(self.score*100))


def find(terms):
    """Use the Lucene index to find monsters"""
    searcher = IndexSearcher(RESOURCE('lucene-data'))
    qp = MultiFieldQueryParser(['name', 'full_text'], StandardAnalyzer())
    qp.setDefaultOperator(MultiFieldQueryParser.Operator.AND)
    fuzzy = [fuzzyQuoteTerm(t) for t in terms]
    terms = ' '.join(fuzzy)
    query = qp.parse(terms)
    hits = searcher.search(query)

    ret = []
    for i, doc in hits:
        ret.append(Hit(doc, hits, i))
        if i == 10:
            break

    return ret


def buildIndex(monsters):
    dataDir = RESOURCE('lucene-data')
    if os.path.exists(dataDir):
        return
    writer = IndexWriter(dataDir, StandardAnalyzer(), True)
    for monster in monsters:
        indexMonster(writer, monster)


class Options(usage.Options):
    def parseArgs(self, *terms):
        self['terms'] = terms

    def postOptions(self):
        for hit in find(self['terms']):
            print hit.name, hit.score




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

