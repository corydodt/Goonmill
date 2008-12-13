"""
Put a Pythonic face on estraiernative
"""

from _estraiernative import (Condition as CCondition,
    Database as CDatabase, Document as CDocument, EstError as CError)

class FlushFailed(Exception):
    """
    Could not remove the specified doc from the database.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class EditFailed(Exception):
    """
    Could not edit the specified doc in the database
    """
    def __init__(self, id, message):
        self.id = id
        self.message = message

    def __str__(self):
        return 'Document %s: %s' % (self.id, self.message)

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


class HCondition(object):
    """
    A search condition.
    Use matching='simple', 'rough', 'union' or 'isect'
    """
    def __init__(self, phrase, matching='simple', max=None, skip=None):
        if type(phrase) is unicode:
            phrase = phrase.encode('utf-8')
        self.condition = CCondition()
        self.condition.set_phrase(phrase)
        if max is not None:
            self.condition.set_max(max)
        if skip is not None:
            self.condition.set_skip(skip)
        flags = 0
        if matching == 'simple':
            flags |= CCondition.SIMPLE
        elif matching == 'rough':
            flags |= CCondition.ROUGH
        elif matching == 'union':
            flags |= CCondition.UNION
        elif matching == 'isect':
            flags |= CCondition.ISECT
        self.condition.set_options(flags)

    def addAttr(self, expression):
        """
        Use 'expression' to filter results by attributes
        """
        if not type(expression) is unicode:
            raise KeyError("expression must be unicode text")
        self.condition.add_attr(expression.encode('utf-8'))

    def setOrder(self, expression):
        """
        Use 'expression' to order results by attributes
        """
        if not type(expression) is unicode:
            raise KeyError("expression must be unicode text")
        self.condition.set_order(expression.encode('utf-8'))


# TODO - @unicodeToByte("argname", ...) to require unicode (and decode it)


class HDatabase(object):
    """
    A more pythonic interface to estraier's database

    With autoflush=True (the default), automatically flush after every
    document add, which simplifies indexing.

    Set autoflush=False to manually flush, which allows better performance
    when indexing lots of documents at once.
    """
    # TODO - pass an optional encoding into __init__ (default utf-8) to
    # specify the desired encoding.  after a database is created, write a
    # special file in it that remembers the encoding.  read that file on
    # opening to set an instance variable.  replace all 'utf-8' with
    # self.encoding in database accesses
    def __init__(self, autoflush=True):
        self._cdb = CDatabase()
        # self.autoflush = autoflush
        self.autoflush = False # FIXME

    def putDoc(self, doc, clean=False, weight=False):
        """
        Add a document to the index
        """
        flags = 0
        if clean:
            flags = flags | self._cdb.PDCLEAN
        if weight:
            flags = flags | self._cdb.PDWEIGHT
        if not self._cdb.put_doc(doc._cdoc, flags):
            msg = self._cdb.err_msg(self._cdb.error())
            raise PutFailed(doc[u'@uri'], msg)

        if self.autoflush:
            self.flush()

        return doc

    def flush(self):
        if not self._cdb.flush(-1):
            msg = self._cdb.err_msg(self._cdb.error())
            raise FlushFailed(msg)

    def remove(self, doc=None, uri=None, id=None):
        """
        Take a document out of the database by reference, by uri or by id
        """
        if uri is None and id is None and doc is None:
            raise TypeError("Either doc, uri or id is required to remove a document")

        flags = 0 # TODO - support ODCLEAN flag
        if hasattr(doc, 'id'):
            id = doc.id
        else:
            if uri is not None:
                id = self._cdb.uri_to_id(uri.encode('utf-8'))
        if not self._cdb.out_doc(id, flags):
            msg = self._cdb.err_msg(self._cdb.error())
            raise EditFailed(id, msg)

    def __delitem__(self, uri):
        return self.remove(uri=uri)

    def updateAttributes(self, doc):
        """
        Edit a document's attributes in-place.  Note: there is no way to edit
        the texts.
        """
        if not self._cdb.edit_doc(doc._cdoc):
            msg = self._cdb.err_msg(self._cdb.error())
            raise EditFailed(doc.id, msg)

    def optimize(self, purge=False, opt=False):
        """
        Perform either a free-space compact operation, or a db optimization,
        or both, or neither, depending on flags.
        """
        flags = (0 if purge else self._cdb.OPTNOPURGE)
        flags = flags | (0 if opt else self._cdb.OPTNODBOPT)
        self._cdb.optimize(flags)

    def __len__(self):
        return self._cdb.doc_num()

    def sync(self):
        """
        ??? If anyone knows what this should do and how it is different from
        flush(), tell me.
        """
        raise NotImplemented("I'll implement this when someone tells me what it does")
        self._cdb.sync() # TODO - needs a unit test

    def open(self, directory, mode):
        """
        Open the database directory.  Only valid modes are 'a', 'r' and 'w'

        'a' corresponds to WRITER | CREAT (created only if it does not exist)
        'w' corresponds to WRITER | CREAT | TRUNC (clobbered if it exists)
        'r' corresponds to READER
        """
        flags = 0
        if mode == 'a':
            flags = self._cdb.DBWRITER | self._cdb.DBCREAT
        elif mode == 'w':
            flags = self._cdb.DBWRITER | self._cdb.DBCREAT | self._cdb.DBTRUNC
        elif mode == 'r':
            flags = self._cdb.DBREADER

        assert flags, "mode must be 'a', 'w' or 'r'"

        if not self._cdb.open(directory, flags):
            msg = self._cdb.err_msg(self._cdb.error())
            raise OpenFailed(msg)

        return self

    def close(self):
        """
        Put the database down for the night.
        """
        failed = False
        try:
            if not self._cdb.close():
                failed = True
        except CError:
            failed = True
        if failed:
            msg = self._cdb.err_msg(self._cdb.error())
            raise CloseFailed(msg)

    def search(self, condition):
        """
        Submit a query to the database and return the results object.
        """
        result = self._cdb.search(condition.condition)
        return HResults(self, result)

    def walkResult(self, result):
        count = result.doc_num()
        for i in range(count):
            doc = self._cdb.get_doc(result.get_doc_id(i), 0) # TODO - flags

            if doc is None: # XXX WTF? is this for a race condition against
                continue    # someone removing docs from the index?

            yield HHit.fromCDocument(doc)

    def __getitem__(self, uri):
        if not type(uri) is unicode:
            raise KeyError("key (uri) must be unicode text")
        uri = uri.encode('utf8')
        id = self._cdb.uri_to_id(uri)
        return HDocument.fromCDocument(self._cdb.get_doc(id, 0))


class HResults(list):
    """
    List wrapper for results of the search.
    """
    def __init__(self, db, result):
        self._cresult = result
        list.__init__(self, db.walkResult(result))

    def hintWords(self):
        """
        Return the unicode-d search terms
        """
        return [w.decode('utf-8') for w in self._cresult.hint_words()]

    def pluck(self, attribute):
        """
        Return the value of the given attribute for each result, in a list
        """
        return [h[attribute] for h in self]


class HDocument(object):
    """
    Dict-like interface to a document
    """
    def __str__(self):
        return self._cdoc.dump_draft()

    def __init__(self, uri):
        if not type(uri) is type(u''):
            raise TypeError("Must provide uri as unicode text")
        self._cdoc = CDocument()
        self._cdoc.add_attr('@uri', uri.encode('utf-8'))

    def addHiddenText(self, text):
        if not type(text) is type(u''):
            raise TypeError("Must provide unicode text")
        t = text.encode('utf-8')
        self._cdoc.add_hidden_text(t)

    def addText(self, text):
        if not type(text) is type(u''):
            raise TypeError("Must provide unicode text")
        t = text.encode('utf-8')
        self._cdoc.add_text(t)

    @classmethod
    def fromCDocument(cls, cdocument):
        self = cls(uri=cdocument.attr('@uri').decode('utf8'))
        self._cdoc = cdocument
        return self

    def __delitem__(self, name):
        raise NotImplemented("Cannot delete attributes from this document")

    def __setitem__(self, name, value):
        if not type(name) is type(value) is type(u''):
            raise TypeError("Must provide unicode key and value")
        v = value.encode('utf-8')
        self._cdoc.add_attr(name, v)

    def __getitem__(self, name):
        name = name.decode('utf-8')
        if name not in self._cdoc.attr_names():
            raise KeyError(name)
        return self._cdoc.attr(name).decode('utf-8')

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return [n.decode('utf-8') for n in self._cdoc.attr_names()]

    def values(self):
        return [self[a] for a in self.keys()]

    def items(self):
        return [(a,self[a]) for a in self.keys()]

    def getTexts(self):
        return map(lambda t: t.decode('utf-8'), self._cdoc.texts())

    def _get_id(self):
        return self._cdoc.id()
    id = property(_get_id)


class HHit(HDocument):
    """
    Dict-like interface to a document
    """
    def teaser(self, terms, format='html'):
        """
        Produce the teaser/snippet text for the hit
        """
        if format != 'html':
            raise NotImplementedError("Only html format supported for teaser text")

        # arguments to make_snippet MUST be byte strings
        bterms = []
        for t in terms:
            if not type(t) is type(u''):
                raise TypeError("Terms must be unicode text")
            bterms.append(t.encode('utf8'))

        # TODO - parameterize make_snippet's numbers
        snip = self._cdoc.make_snippet(bterms, 120, 35, 35)

        # parse the newline-delimited snippet format
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
