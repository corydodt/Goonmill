"""PyLucene-based indexing and searching
"""
# vi:ft=python
import sys, os

import re
rc = re.compile

from PyLucene import (IndexWriter, StandardAnalyzer, Document, Field,
        MultiFieldQueryParser, IndexSearcher)

from twisted.web import microdom, domhelpers
from twisted.python import usage

import magic

def indexDirectory(writer, dir):
    for dirname, dirs, files in os.walk(dir):
        for f in files:
            indexFile(writer, dirname, f)

def indexFile(writer, dir, filename):
    path = os.path.join(dir, filename)

    try:
        magicType = Identifier.identify(path)
        reader = Identifier.textReader(path, magicType)
    except EnvironmentError, e:
        print e
        return

    if reader is None:
        print "x",
        return
    else:
        print ".",

    data = reader(file(path).read())

    doc = Document()
    basename = Field("basename", filename,
                  Field.Store.YES, Field.Index.TOKENIZED)
    basename.setBoost(2.0)
    body = Field("body", data,
                  Field.Store.YES, Field.Index.TOKENIZED)
    doc.add(basename)
    doc.add(body)

    writer.addDocument(doc)


def textFromHtml(htmlText):
    d = microdom.parseString(htmlText, beExtremelyLenient=1)
    s = domhelpers.gatherTextNodes(d, joinWith=" ")
    ## print '\n'.join('| ' + l for l in s.splitlines())
    return s


magicCookie = magic.open(magic.MAGIC_NONE)
magicCookie.load()

identity = lambda x: x


ALWAYS_SKIP = object()

class Identifier(object):
    """
    Identify a file as belonging to an index-able type.
    """
    # i[0] is a pattern to match against the returned value of magicCookie.
    # i[1] is the function to call to get the text out.
    typeMap = [
        (rc(r'XML .* document text'), textFromHtml),
        (rc(r'HTML document text'), identity),
        (rc(r'ASCII (English )?text\b.*'), identity),
    ]

    extensionMap = {'.html': textFromHtml,
            '.xhtml': textFromHtml,
            '.txt': identity,
            '.svg': ALWAYS_SKIP,
            '.dja': ALWAYS_SKIP,
            }


    @classmethod
    def identify(cls, filename):
        """Return the magic type"""
        buf = file(filename).read(4096)
        return magicCookie.buffer(buf)

    @classmethod
    def textReader(cls, filename, magicType):
        """Return a function to call to read this type's data as plain text
        strings
        """
        # look at extensions first.  some of them can fool libmagic
        left, extn = os.path.splitext(filename)
        extn = extn.lower()
        override = cls.extensionMap.get(extn)
        if callable(override):
            return override
        elif override is ALWAYS_SKIP:
            return None

        for rex, fn in cls.typeMap:
            if rex.match(magicType):
                return fn

        return None


class Query(usage.Options):
    synopsis = 'index query "your search.."'
    def parseArgs(self, *terms):
        self['terms'] = terms

    def postOptions(self):
        searcher = IndexSearcher('out')
        qp = MultiFieldQueryParser(['basename', 'body'], StandardAnalyzer())
        qp.setDefaultOperator(MultiFieldQueryParser.Operator.AND)
        terms = ' '.join(self['terms'])
        query = qp.parse(terms, )
        hits = searcher.search(query)

        for i, doc in hits:
            print doc.basename.stringValue(), '(%s)' % (hits.score(i),)
            #for field in doc:
            #    print field.name(), field.stringValue()


class Build(usage.Options):
    synopsis = 'index build <dirs>...'
    def parseArgs(self, *dirs):
        self['dirs'] = dirs

    def postOptions(self):
        writer = IndexWriter('out', StandardAnalyzer(), True)
        for dir in self['dirs']:
            indexDirectory(writer, dir)


class Options(usage.Options):
    subCommands = [
            ['query', None, Query, 'Query the index'],
            ['build', None, Build, 'Build the index'],
            ]


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

