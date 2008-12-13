from __future__ import with_statement

import unittest
import os
from contextlib import contextmanager

import hypy

from hypy import (HDocument, HDatabase, HHit, HResults, HCondition, OpenFailed,
        PutFailed, CloseFailed, FlushFailed, EditFailed)

class TestHDocument(unittest.TestCase):
    def setUp(self):
        self.doc = HDocument(uri=u'1')

    def test_dictlike(self):
        """
        HDocument mostly conforms to the dictionary protocol.  Make sure that
        works. 
        """
        doc = self.doc

        # byte strings, other types are not allowed.
        self.assertRaises(TypeError, doc.__setitem__, 'foobar', 'baz')
        self.assertRaises(TypeError, doc.__setitem__, 'foobar', 1)

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


class TestDatabase(unittest.TestCase):
    """
    Tests HResults, HCondition and HHit.  And since you can't test these
    things without a database, test HDatabase.
    """
    @contextmanager
    def freshenDatabase(self, extras=0):
        """
        Use:
            with self.freshenDatabase() as db:
                ... stuff that should test using these three documents ...
        """
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

        for x in range(4, extras+4):
            doc = HDocument(uri=unicode(x))
            doc.addText(u'filler filler filler carrot top')
            # set some attributes for attribute operator testing
            doc[u'specialId'] = unicode(x)
            doc[u'description'] = unicode(x) * x
            doc[u'date'] = u'2008-12-%s' % (x,)
            db.putDoc(doc)

        db.flush()

        try:
            yield db
        finally:
            try:
                db.close()
            except CloseFailed:
                """Some of the tests do this close on their own."""

    def test_dbOptimize(self):
        """
        Make sure the various optimize flags do not cause a heart attack.
        """
        with self.freshenDatabase() as db:
            db.optimize(purge=True)
        with self.freshenDatabase() as db:
            db.optimize(opt=True)
        with self.freshenDatabase() as db:
            db.optimize()

    def test_removeUpdate(self):
        """
        Test for document id, update, document removal, len() of database.
        """
        docxx = HDocument(uri=u'xx')
        docxx.addText(u'xx')

        # id of a non-stored document
        self.assertEqual(docxx.id, -1)

        # removes and updates
        with self.freshenDatabase() as db:
            # flags; just test that these do not nuke us. no idea what they
            # are supposed to do.
            db.putDoc(docxx, clean=True)
            del db[u'xx']
            # delete same doc twice?
            self.assertRaises(EditFailed, db.remove, uri=u'xx')

            db.putDoc(docxx)

            # __len__
            self.assertEqual(len(db), 4)

            # remove by uri, by id, by reference
            db.remove(uri=u'1')
            self.assertEqual(len(db), 3)
            doc2 = db[u'2']
            db.remove(doc2)
            self.assertEqual(len(db), 2)
            doc3id = db[u'3'].id
            db.remove(id=doc3id)
            self.assertEqual(len(db), 1)
            # no arg?
            self.assertRaises(TypeError, db.remove)
            # already removed?
            self.assertRaises(EditFailed, db.remove, id=doc3id)

            # fetch a document from the database, edit it, store it, compare
            # it with the original (unfetched) document.  Verify that they are
            # different after the edit. Then verify that the document can be
            # fetched (again) from the database with the edited text.
            dbdocxx = db[u'xx']
            # yes, these are different objects
            self.assertFalse(docxx is dbdocxx)
            self.assertTrue(dbdocxx.get(u'zz') is None)

            dbdocxx[u'zz'] = u'hello'
            db.updateAttributes(dbdocxx)
            dbdocxx2 = db[u'xx']
            # again, different objects
            self.assertFalse(dbdocxx is dbdocxx2)
            self.assertEqual(dbdocxx2.get(u'zz'), u'hello')

    def test_putFlags(self):
        """
        Tests for put flags, other put-related corner cases.
        """
        docxx = HDocument(uri=u'xx')
        docxx.addText(u'xx')

        with self.freshenDatabase() as db:
            # flags; just test that these do not nuke us. no idea what they
            # are supposed to do.
            db.putDoc(docxx, clean=True)
            del db[u'xx']
            db.putDoc(docxx, weight=True)
            del db[u'xx']

            ## # put same doc twice?
            ## apparently this works. huh.
            ## db.putDoc(docxx); db.putDoc(docxx)

    def test_condExtras(self):
        """
        Tests for search skip, search options, cond on attributes
        """
        with self.freshenDatabase(extras=10) as db:
            self.assertEqual(len(db), 13)
            # skip and max
            cond4_8 = HCondition(u'filler', max=5)
            cond9_11 = HCondition(u'filler', max=3, skip=5)
            res1 = db.search(cond4_8)
            self.assertEqual(res1.pluck(u'@uri'), list(u'45678'))
            res2 = db.search(cond9_11)
            self.assertEqual(res2.pluck(u'@uri'), [u'9', u'10', u'11'])

            # union matching
            result = db.search(HCondition('ipsum score', matching='simple'))
            self.assertEqual(len(result), 0)
            result = db.search(HCondition('ipsum score', matching='union'))
            self.assertEqual(len(result), 2)

            # fewer-than-max hits
            result = db.search(HCondition('7*', matching='simple', max=2))
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][u'@uri'], u'3')

            # attribute conditions
            def attrSearch(expr, order=None):
                cond = HCondition(u'*.**') # regular expression match, all characters
                cond.addAttr(expr)
                if order:
                    cond.setOrder(order)
                return db.search(cond)
            result = attrSearch(u'description STREQ 4444')
            self.assertEqual(result.pluck(u'@uri'), [u'4'])
            result = attrSearch(u'specialId NUMGE 10')
            self.assertEqual(result.pluck(u'@uri'), [u'10', u'11', u'12', u'13'])
            result = attrSearch(u'date NUMGE 2008-12-09')
            self.assertEqual(result.pluck(u'@uri'), [u'9', u'10', u'11', u'12', u'13'])
            result = attrSearch(u'description STRRX .{10,14}')
            self.assertEqual(result.pluck(u'@uri'), [u'10', u'11', u'12', u'13'])
            # ordering and !not
            result = attrSearch(u'description !STRRX .{10,14}', u'@uri NUMA')
            self.assertEqual(result.pluck(u'@uri'), list(u'123456789'))
            result = attrSearch(u'description STRRX .{10,14}', u'@uri NUMD')
            self.assertEqual(result.pluck(u'@uri'), [u'13', u'12', u'11', u'10'])

    def test_dbOpenClosed(self):
        """
        Tests for all the db open/close modes
        """
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
        db.open('_temp_db', 'w')
        self.assert_(os.path.exists('_temp_db/_idx'))
        db.putDoc(docyy)
        db.close()

        # r mode
        db.open('_temp_db', 'r')
        # write to read-only db
        self.assertRaises(PutFailed, db.putDoc, docxx)
        self.assertEqual(len(db.search(condyy)), 1)
        db.close()

        # a mode
        db.open('_temp_db', 'a')
        db.putDoc(docxx)
        db.flush()
        self.assertEqual(len(db.search(condxx)), 1)
        self.assertEqual(len(db.search(condyy)), 1)
        db.close()

        # w mode again - check that the db is clobbered
        db.open('_temp_db', 'w')
        self.assertEqual(len(db.search(condxx)), 0)
        db.close()

        # close after successful close
        self.assertRaises(CloseFailed, db.close)

    def test_queries(self):
        """
        Test various conditions against an index to make sure search works.
        """
        with self.freshenDatabase() as db:
            # plain search, 8-bit str
            result = db.search(HCondition('wor*', matching='simple'))
            self.assertEqual(len(result), 3)

            # unicode searches
            result = db.search(HCondition(u'wor*', matching='simple'))
            self.assertEqual(len(result), 3)

            # test simple query with multiple hits
            result = db.search(HCondition('res*', matching='simple'))
            self.assertEqual(result.pluck('@uri'), [u'1', u'2'])

            # vary query terms to check result scoring
            result = db.search(HCondition('someth* | whatever*', matching='simple', max=2))
            self.assertEqual(result.pluck(u'@uri'), [u'2', u'3'])
            result = db.search(HCondition('someth* | upon*', matching='simple', max=2))
            self.assertEqual(result.pluck(u'@uri'), [u'3', u'2']) # FIXME

