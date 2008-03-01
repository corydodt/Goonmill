import sys, os, shutil
from itertools import count

from lucene import (IndexWriter, StandardAnalyzer, Document, Field,
        MultiFieldQueryParser, IndexSearcher, initVM, CLASSPATH, Hit,
        FSDirectory, QueryParser)
initVM(CLASSPATH)

DIRECTORY = 'xxindex'
STORE = FSDirectory.getDirectory(DIRECTORY, True)

def indexDoc(writer, d):
    doc = Document()
    name_ = Field("name_", d.name,
                  Field.Store.YES, Field.Index.TOKENIZED)
    name_.setBoost(2.0)
    full_text = Field("full_text", d.full,
                  Field.Store.YES, Field.Index.TOKENIZED)
    id = Field("id", str(d.id),
                  Field.Store.YES, Field.Index.UN_TOKENIZED)
    doc.add(name_)
    doc.add(full_text)
    doc.add(id)

    writer.addDocument(doc)


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
    searcher = IndexSearcher(STORE)
    qp = QueryParser('full_text', StandardAnalyzer())
    terms = ' '.join(terms)
    query = qp.parse(terms)
    hits = searcher.search(query)

    ret = []
    for i, hit in enumerate(hits):
        doc = Hit.cast_(hit).getDocument()
        ret.append(MyHit(doc, hits, i))
        if i == 10:
            break

    return ret


def buildIndex(docs):
    try:
        shutil.rmtree(DIRECTORY)
    except Exception, e:
        pass

    analyzer = StandardAnalyzer()
    writer = IndexWriter(STORE, analyzer, True)
    for doc in docs:
        indexDoc(writer, doc)
    writer.optimize()
    writer.close()


class MyDoc(object):
    counter = count()
    def __init__(self, s):
        name, rest = s.split(None, 1)
        self.name = name
        self.full = rest
        self.id = MyDoc.counter.next()

    def __repr__(self):
        return '<MyDoc %s>' % (self.name,)


if __name__ == '__main__':
    buildIndex(map(MyDoc, [
        'demon this is a test', 
        'dragon test number 2',
        'skeleton ha ha ha ha',
        ]))
    for hit in find(sys.argv[1:]):
        print hit.name, hit.score

