"""PyLucene-based indexing and searching """
# vi:ft=python
import sys, os
import shutil
import re

import lucene
lucene.initVM(lucene.CLASSPATH)

from twisted.web import microdom, domhelpers
from twisted.python import usage

from goonmill.util import RESOURCE
INDEX_DIRECTORY = RESOURCE('lucene-data')

slashRx = re.compile(r'\\([n"])')

def repSlash(m):
    if m.group(1) == 'n':
        return '\n'
    return m.group(1)

def indexMonster(writer, monster):
    _ft = re.sub(slashRx, repSlash, monster.full_text)
    full = textFromHtml(_ft)

    doc = lucene.Document()
    name_ = lucene.Field("name_", monster.name,
                  lucene.Field.Store.YES, lucene.Field.Index.TOKENIZED)
    name_.setBoost(2.0)
    full_text = lucene.Field("full_text", full,
                  lucene.Field.Store.YES, lucene.Field.Index.TOKENIZED)
    id = lucene.Field("id", str(monster.id),
                  lucene.Field.Store.YES, lucene.Field.Index.UN_TOKENIZED)
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


class MyHit(object):
    """One monster search result
    Essentially an adapter for Lucene's hits
    """
    def __init__(self, doc, hits, index):
        self.name = doc['name_']
        self.id = doc['id']
        self.score = hits.score(index)

    def __repr__(self):
        return "<MyHit name=%s %s%%>" % (self.name, int(self.score*100))


def find(terms):
    """Use the Lucene index to find monsters"""
    fuzzy = [fuzzyQuoteTerm(t) for t in terms]
    terms = ' '.join(fuzzy)
    dataDir = lucene.FSDirectory.getDirectory(INDEX_DIRECTORY, False)
    searcher = lucene.IndexSearcher(dataDir)

    MFQP = lucene.MultiFieldQueryParser

    SHOULD = lucene.BooleanClause.Occur.SHOULD

    query = MFQP.parse(terms, 
            ['name_', 'full_text'], 
            [SHOULD, SHOULD], 
            lucene.StandardAnalyzer())

    hits = searcher.search(query)

    ret = []
    for i, hit in enumerate(hits):
        doc = lucene.Hit.cast_(hit).getDocument()
        ret.append(MyHit(doc, hits, i))
        if i == 10:
            break

    return ret


def buildIndex(monsters):
    if os.path.exists(INDEX_DIRECTORY):
        return
    dataDir = lucene.FSDirectory.getDirectory(INDEX_DIRECTORY, True)
    writer = lucene.IndexWriter(dataDir, lucene.StandardAnalyzer(), True)
    for monster in monsters:
        indexMonster(writer, monster)
    writer.optimize()
    writer.close()


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

        try:
            for hit in find(self['terms']):
                print hit.name, hit.score
        except lucene.JavaError, e:
            if 'FileNotFoundException' in str(e):
                raise usage.UsageError(
                        "** Missing index directory.  Run with --build-index")




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

