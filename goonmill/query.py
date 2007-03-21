"""
Query the XML database of monsters for matching monsters.
"""

import sqlalchemy as S

from goonmill.util import RESOURCE

class Monster(object):
    """A Monster mapped from the db"""

    def __repr__(self):
        return '<%s name=%s>' % (self.__class__.__name__, self.name)

class SRDDatabase(object):
    """A complete SRD database"""
    def __init__(self):
        self.meta = S.DynamicMetaData()
        self.engine = S.create_engine('sqlite:///' + RESOURCE('srd35.db'))
        self.meta.connect(self.engine)

        self.monster = S.Table('monster', self.meta, autoload=True)
        S.mapper(Monster, self.monster)

        self.monster_text = S.Table('monster_text', self.meta, autoload=True)

    def lookup(self, id):
        """Return the Monster for this id by querying the sqlite database"""
        ss = S.create_session(self.engine)
        return ss.query(Monster).get(id)

    def find(self, terms):
        """
        Look up a monster in monster_text and return the Monster objects
        corresponding to those hits.
        """
        m = self.monster.c
        t = self.monster_text.c
        clauses = [t.data.like('%%%s%%' % (term,)) for term in terms]

        _likeClauses = S.and_(*clauses)
        _monsterSelect = S.and_(m.id==t.id, _likeClauses)

        ss = S.create_session(self.engine)
        return ss.query(Monster).select(_monsterSelect)

db = SRDDatabase()

def lookup(id):
    """Return the Monster for this id"""
    return db.lookup(id)

def find(terms):
    """Return the Monsters that contain these terms"""
    return db.find(terms)
