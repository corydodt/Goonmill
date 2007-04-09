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

        self.monster = S.Table('monster', self.meta, autoload=True)
        S.mapper(Monster, self.monster)

        self.skill = S.Table('skill', self.meta, autoload=True)
        S.mapper(Skill, self.skill)

        self.monster_text = S.Table('monster_text', self.meta, autoload=True)

        self.feat = S.Table('feat', self.meta, autoload=True)
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

    def lookupSkill(self, idOrName):
        """Return the Skill for this id or name"""
        ss = S.create_session(self.engine)
        skill = ss.query(Skill).get(idOrName)
        if skill is None:
            skill = ss.query(Skill).get_by(name=idOrName)
        return skill

    def lookupFeat(self, idOrName):
        """Return the Feat for this id or name"""
        ss = S.create_session(self.engine)
        feat = ss.query(Feat).get(idOrName)
        if feat is None:
            feat = ss.query(Feat).get_by(name=idOrName)
        return feat

    def _allSkillStats(self):
        """Return all skill names as strings"""
        ss = S.create_session(self.engine)
        return [m.skills for m in ss.query(Monster)]

    def _allFeatStats(self):
        """Return all feat names as strings"""
        ss = S.create_session(self.engine)
        return [m.feats for m in ss.query(Monster)]

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

def _allMonsters():
    return db._allMonsters()
