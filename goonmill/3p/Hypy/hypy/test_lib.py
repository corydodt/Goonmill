import unittest
import os

from hypy import (HDocument, HDatabase, HHit, HResults, HCondition, OpenFailed,
        PutFailed, CloseFailed)

class TestHDocument(unittest.TestCase):
    def setUp(self):
        self.doc = HDocument(uri=u'1')

    def test_dictlike(self):
        doc = self.doc

        self.assertRaises(TypeError, doc.__setitem__, 'foobar', 'baz')

        doc[u'foobar'] = u'baz'
        doc[u'foobar']
        self.assertEqual(doc[u'foobar'], u'baz')
        self.assertEqual(doc.get('foobar', 'default'), u'baz')
        self.assertEqual(doc.get('xyz', 'default'), 'default')
        self.assertEqual(doc.get('xyz'), None)

        newattrs = {u'new1': u'lala', u'foobar': u'bazz'}
        doc.update(newattrs)
        self.assertEqual(sorted(doc.items()), [(u'@uri', u'1'), (u'foobar', u'bazz'), (u'new1',
            u'lala')])

        doc[u'ninjas'] = u'11'
        self.assertEqual(sorted(doc.keys()), [u'@uri', u'foobar', u'new1', u'ninjas', ])
        self.assertEqual(sorted(doc.values()), [u'1', u'11', u'bazz', u'lala'])

    def test_text(self):
        doc = self.doc
        self.assertRaises(TypeError, doc.addText, 'xyz')
        doc.addText(u'xyz')
        self.assertEqual([u'xyz'], doc.getTexts())
        doc.addText(u'123')
        self.assertEqual([u'xyz', u'123'], doc.getTexts())
        self.assertRaises(TypeError, doc.addHiddenText, 'abc')
        doc.addHiddenText(u'abc')
        self.assertEqual([u'xyz', u'123'], doc.getTexts())


class TestQueries(unittest.TestCase):
    """
    Tests HResults, HCondition and HHit.  And since you can't test these
    things without a database, test HDatabase.
    """
    def freshenDatabase(self):
        db = HDatabase()
        db.open('_temp_db', 'w')

        doc = HDocument(uri=u'1')
        doc.addText(u'word this is my document. do you like documents? this one is hi-res.')
        db.putDoc(doc, clean=True)

        doc = HDocument(uri=u'2')
        doc.addText(u'word lorem ipsum dolor sit amet something whatever whatever i do not remember the rest')
        db.putDoc(doc)

        doc = HDocument(uri=u'3')
        doc.addText(u'word four score and 7 years ago our forefathers brought forth upon upon something')
        db.putDoc(doc)

        db.flush()

        return db

    def test_dbExtras(self):
        """
        Tests for put flags, document removal, document id, optimization,
        len() of database
        """
        self.freshenDatabase()
        db.putDoc
        TODO

    def test_condExtras(self):
        """
        Tests for search skip, cond options, cond on attributes
        """
        TODO

    def test_dbOpenClosed(self):
        docyy = HDocument(uri=u'yy')
        docyy.addText(u'yy')
        docxx = HDocument(uri=u'xx')
        docxx.addText(u'xx')
        condxx = HCondition(u'xx')
        condyy = HCondition(u'yy')

        db = HDatabase()
        # open of unreachable directory
        self.assertRaises(OpenFailed, db.open, 'does/not/exist', 'a')
        # close before successful open
        self.assertRaises(CloseFailed, db.close)

        # w mode
        db.open('_test_db', 'w')
        self.assert_(os.path.exists('_test_db/_idx'))
        db.putDoc(docyy)
        db.close()

        # r mode
        db.open('_test_db', 'r')
        # write to read-only db
        self.assertRaises(PutFailed, db.putDoc, docxx)
        self.assertEqual(len(db.search(condyy)), 1)
        db.close()

        # a mode
        db.open('_test_db', 'a')
        db.putDoc(docxx)
        db.flush()
        self.assertEqual(len(db.search(condxx)), 1)
        self.assertEqual(len(db.search(condyy)), 1)
        db.close()

        # w mode again - check that the db is clobbered
        db.open('_test_db', 'w')
        self.assertEqual(len(db.search(condxx)), 0)
        db.close()

        # close after successful close
        self.assertRaises(CloseFailed, db.close)

    def test_queries(self):
        db = self.freshenDatabase()

        # plain search, 8-bit str
        result = db.search(HCondition('wor*', matching='simple'))
        self.assertEqual(len(result), 3)

        # unicode searches
        result = db.search(HCondition(u'wor*', matching='simple'))
        self.assertEqual(len(result), 3)

        # max
        result = db.search(HCondition('wor*', matching='simple', max=1))
        self.assertEqual(len(result), 1)

        # test simple query with multiple hits
        result = db.search(HCondition('res*', matching='simple'))
        self.assertEqual(result.pluck('@uri'), [u'1', u'2'])

        # test fewer-than-max hits
        result = db.search(HCondition('7*', matching='simple', max=2))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][u'@uri'], u'3')

        # vary query terms to check result scoring
        result = db.search(HCondition('someth* | whatever*', matching='simple', max=2))
        self.assertEqual(result.pluck(u'@uri'), [u'2', u'3'])
        result = db.search(HCondition('someth* | upon*', matching='simple', max=2))
        self.assertEqual(result.pluck(u'@uri'), [u'3', u'2']) # FIXME

