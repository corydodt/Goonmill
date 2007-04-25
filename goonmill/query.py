"""
Query the XML database of monsters for matching monsters.
"""

import sqlalchemy as S

from goonmill.util import RESOURCE

class Monster(object):
    """A Monster mapped from the db"""

    def __repr__(self):
        return '<%s name=%s>' % (self.__class__.__name__, self.name)


class Skill(object):
    """A skill mapped from the db"""


class Feat(object):
    """A skill mapped from the db"""

    def __repr__(self):
        return "<Feat %s>" % (self.name,)


class SRDDatabase(object):
    """A complete SRD database"""
    def __init__(self):
        self.meta = S.DynamicMetaData()
        self.engine = S.create_engine('sqlite:///' + RESOURCE('srd35.db'))
        self.meta.connect(self.engine)

        table = lambda name: S.Table(name, self.meta, autoload=True)

        self.monster = table('monster')
        S.mapper(Monster, self.monster)

        self.skill = table('skill')
        S.mapper(Skill, self.skill)

        self.monster_text = table('monster_text')

        self.feat = table('feat')
        S.mapper(Feat, self.feat)

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

    def genericLookup(self, mapper, idOrName):
        """
        Implement the dual-interpretation logic for "idOrName" to look
        up an object from the database by id or by name.  Naturally
        this requires the table have a 'name' column.
        
        @return an instance of the table-mapped class, e.g. Feat or Skill
        """
        ss = S.create_session(self.engine)
        thing = ss.query(mapper).get(idOrName)
        if thing is None:
            thing = ss.query(mapper).get_by(name=idOrName)
        return thing

    def lookupFeat(self, idOrName):
        """A Feat for this id or name"""
        return self.genericLookup(Feat, idOrName)

    def lookupSkill(self, idOrName):
        """A Skill for this id or name"""
        return self.genericLookup(Skill, idOrName)

    def _allSkillStats(self):
        """Return all skill names as strings"""
        ss = S.create_session(self.engine)
        return [m.skills for m in ss.query(Monster)]

    def _allHPStats(self):
        """Return all hit dice as strings"""
        ss = S.create_session(self.engine)
        return [m.hit_dice for m in ss.query(Monster)]

    def _allFeatStats(self):
        """Return all feat names as strings"""
        ss = S.create_session(self.engine)
        return [m.feats for m in ss.query(Monster)]

    def _allAttackStats(self):
        """Return all attacks for all monsters"""
        ss = S.create_session(self.engine)
        return [(m.id, m.full_attack) for m in ss.query(Monster)]

    def _allSaveStats(self):
        """Return all save names as strings"""
        ss = S.create_session(self.engine)
        return [m.saves for m in ss.query(Monster)]

    def _allMonsters(self):
        ss = S.create_session(self.engine)
        return ss.query(Monster)

db = SRDDatabase()

def lookup(id):
    """Return the Monster for this id"""
    return db.lookup(id)

def find(terms):
    """Return the Monsters that contain these terms"""
    return db.find(terms)

def lookupSkill(idOrName):
    """Return the Skill for this id or name"""
    return db.lookupSkill(idOrName)

def lookupFeat(idOrName):
    """Return the Feat for this is or name"""
    return db.lookupFeat(idOrName)

def _allSkillStats():
    """Return the skill attribute for every monster"""
    return db._allSkillStats()

def _allFeatStats():
    """Return the feat attribute for every monster"""
    return db._allFeatStats()

def _allSaveStats():
    """Return the save attribute for every monster"""
    return db._allSaveStats()

def _allAttackStats():
    """Return the full_attack attribute for every monster"""
    return db._allAttackStats()

def _allMonsters():
    return db._allMonsters()

def _allHPStats():
    return db._allHPStats()
