"""
Put a Pythonic face on estraiernative
"""

from _estraiernative import (Condition as CCondition,
    Database as CDatabase, Document as CDocument)

class PutFailed(Exception):
    """
    Could not add the specified doc to the database.
    """
    def __init__(self, uri, message):
        self.uri = uri
        self.message = message

    def __str__(self):
        return 'Document %s: %s' % (self.uri, self.message)

class OpenFailed(Exception):
    """
    Could not open the database with the specified mode.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class CloseFailed(Exception):
    """
    Could not close the database.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ECondition(object):
    """
    A search condition.
    Use matching='simple', 'rough', 'union' or 'isect'
    """
    def __init__(self, phrase, matching='simple', max=None):
        self.condition = CCondition()
        self.set_phrase(phrase)
        if max is not None:
            self.set_max(max)
        flags = 0
        if matching == 'simple':
            flags |= CCondition.SIMPLE
        elif matching == 'rough':
            flags |= CCondition.ROUGH
        elif matching == 'union':
            flags |= CCondition.UNION
        elif matching == 'isect':
            flags |= CCondition.ISECT
        self.set_options(flags)

    def __getattr__(self, name):
        return getattr(self.condition, name)


class EDatabase(object):
    """
    A more pythonic interface to estraier's database
    """
    def __init__(self):
        self.database = CDatabase()

    def __getattr__(self, name):
        return getattr(self.database, name)

    def putDoc(self, doc, clean=False, weight=False):
        """
        Add a document to the index
        """
        flags = 0
        if clean:
            flags = flags | self.PDCLEAN
        if weight:
            flags = flags | self.PDWEIGHT
        if not self.put_doc(doc, flags):
            msg = self.err_msg(self.error())
            raise EstraierPutFailed(doc.attr('@uri'), msg)

        return doc

    def open(self, directory, mode):
        """
        Open the database directory.  Only valid modes are 'a', 'r' and 'w'

        'a' corresponds to WRITER | CREAT (created only if it does not exist)
        'w' corresponds to WRITER | CREAT | TRUNC (clobbered if it exists)
        'r' corresponds to READER
        """
        flags = 0
        if mode == 'a':
            flags = self.DBWRITER | self.DBCREAT
        elif mode == 'w':
            flags = self.DBWRITER | self.DBCREAT | self.DBTRUNC
        elif mode == 'r':
            flags = self.DBREADER

        assert flags, "mode must be 'a', 'w' or 'r'"

        if not self.database.open(directory, flags):
            msg = self.err_msg(self.error())
            raise OpenFailed(msg)

        return self

    def close(self):
        """
        Put the database down for the night.
        """
        if not self.database.close():
            msg = self.err_msg(self.error())
            raise CloseFailed(msg)

    def search(self, condition):
        """
        Submit a query to the database and return the results object.
        """
        result = self.database.search(condition.condition)
        return EResults(self, result)


class EResults(list):
    """
    List wrapper for results of the search.
    """
    def __init__(self, db, result):
        l = []
        count = result.doc_num()
        for i in range(count):
            doc = db.get_doc(result.get_doc_id(i), 0) # TODO - flags

            if doc is None: # XXX WTF? is this for a race condition against
                            # someone removing docs from the index?
                continue

            l.append(EHit(doc, result.hint_words()))
        list.__init__(self, l)


class EHit(object):
    """
    Dict-like interface to a document returned from a search
    """
    def __getattr__(self, name):
        return getattr(self.hit, name)

    def __init__(self, hit, terms):
        self.hit = hit
        self.terms = terms

    def __getitem__(self, name):
        return self.attr(name)

    def teaser(self, terms, format='html'):
        """
        Produce the teaser/snippet text for the hit
        """
        if format != 'html':
            raise NotImplementedError("Only html format supported for teaser text")
        # arguments to make_snippet MUST be byte strings
        terms = [t.encode('utf8') for t in terms]
        snip = self.make_snippet(terms, 120, 35, 35)
        bunches = snip.split('\n\n')

        strings = []
        for bunch in snip.split('\n\n'):
            _bitStrings = []
            for bit in bunch.split('\n'):
                if '\t' in bit:
                    _bitStrings.append('<strong>%s</strong>' %
                            (bit.split('\t')[0],))
                else:
                    _bitStrings.append(bit)
            strings.append(''.join(_bitStrings))

        decode = lambda s: unicode(s, 'utf8')
        snip = u' ... '.join(map(decode, strings))
        return snip
