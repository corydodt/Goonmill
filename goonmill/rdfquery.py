from twisted.python import log

from playtools import sparqly as S

from rdflib.Namespace import Namespace as NS

from goonmill.util import RESOURCE

FAM = NS('http://goonmill.org/2007/family.n3#')
CHAR = NS('http://goonmill.org/2007/characteristic.n3#')
DICE = NS('http://goonmill.org/2007/dice.n3#')
PCCLASS = NS('http://goonmill.org/2007/pcclass.n3#')
PROP = NS('http://goonmill.org/2007/property.n3#')
SKILL = NS('http://goonmill.org/2007/skill.n3#')
FEAT = NS('http://goonmill.org/2007/feat.n3#')

DB_LOCATION = RESOURCE('rdflib.db')

class SpecialArmorClass(S.SparqItem):
    """Permanent, racial modifier to armor class"""


class Aura(S.SparqItem):
    """Permanent effect that extends some distance around the body of the 
    creature.
    """


class SpecialAction(S.SparqItem):
    """Something a creature can do besides attack"""


class AttackEffect(S.SparqItem):
    """Some type of damage such as cold or non-magical"""


class Resistance(S.SparqItem):
    """A resistance possessed by monsters"""
    attackEffect = S.Ref(AttackEffect,
            "SELECT ?ae { $key ?ae [] }")
    amount = S.Literal("SELECT ?a { ?ae a c:AttackEffect . $key ?ae ?a }")

    def __repr__(self):
        return '<%s to %s>' % (self.__class__.__name__, self.attackEffect[0].label)


class Vulnerability(S.SparqItem):
    """A vulnerability possessed by monsters"""


class Immunity(S.SparqItem):
    """An immunity possessed by monsters"""


class Sense(S.SparqItem):
    """A notable sense possessed by monsters, such as darkvision"""
    range = S.Literal('SELECT ?r { $key p:range ?r }')


class Language(S.SparqItem):
    """A language understood by monsters"""


class SpecialAbility(S.SparqItem):
    """A notable ability of any kind that isn't a standard combat mechanic"""


class SpecialQuality(S.SparqItem):
    """A notable quality possessed by the creature that is always on"""


class CombatMechanic(S.SparqItem):
    """A special combat mechanic that applies to this creature"""


class Family(S.SparqItem):
    """A family of monster with shared characteristics"""
    senses = S.Ref(Sense, 
        'SELECT ?s { $key p:sense ?s }')
    specialAbilities = S.Ref(SpecialAbility, 
        'SELECT ?spec { ?spec a c:SpecialAbility . $key p:miscTrait ?spec }')
    specialQualities = S.Ref(SpecialQuality, 
        'SELECT ?spec { ?spec a c:SpecialQuality . $key p:miscTrait ?spec }')
    combatMechanics = S.Ref(SpecialQuality, 
        'SELECT ?spec { ?spec a c:CombatMechanic . $key p:miscTrait ?spec }')
    languages = S.Ref(Language,
        'SELECT ?lng { $key p:language ?lng }')
    immunities = S.Ref(Immunity,
        'SELECT ?i { $key p:immunity ?i }')
    resistances = S.Ref(Resistance,
        'SELECT ?r { $key p:resistance ?r }')
    vulnerabilities = S.Ref(Vulnerability,
        'SELECT ?r { $key p:vulnerabilities ?r }')


class Ability(S.SparqItem):
    """An ability score"""


class SkillSynergy(S.SparqItem):
    """A skill synergy"""
    bonus = S.Literal('SELECT ?n { $key p:bonus ?n }')
    synergyComment = S.Literal('SELECT ?c { $key p:synergyComment ?c }')


class Skill(S.SparqItem):
    """A skill usable by monsters, such as Diplomacy"""
    keyAbility = S.Ref(Ability, 'SELECT ?k { ?k a c:AbilityScore . $key p:keyAbility ?k }')
    synergy = S.Ref(SkillSynergy, 'SELECT ?s { $key p:synergy ?s }')

    additional = S.Literal('SELECT ?a { $key p:additional ?a }')
    epicUse = S.Literal('SELECT ?a { $key p:epicUse ?a }')
    skillAction = S.Literal('SELECT ?a { $key p:skillAction ?a }')
    skillCheck = S.Literal('SELECT ?a { $key p:skillCheck ?a }')
    tryAgainComment = S.Literal('SELECT ?a { $key p:tryAgainComment ?a }')
    untrained = S.Literal('SELECT ?a { $key p:untrained ?a }')

SkillSynergy.otherSkill = S.Ref(Skill, 'SELECT ?s { $key p:fromSkill ?s }')


class Feat(S.SparqItem):
    """A feat usable by monsters, such as Weapon Focus"""
    stackable = S.Boolean(
            'ASK { $key a c:StackableFeat }')
    canTakeMultiple = S.Boolean(
            'ASK { $key a c:CanTakeMultipleFeat }')
    epic = S.Boolean(
            'ASK { $key a c:EpicFeat}')
    psionic = S.Boolean(
            'ASK { $key a c:PsionicFeat }')
    isArmorClassFeat = S.Boolean(
            'ASK { $key a <http://goonmill.org/2009/statblock.n3#ArmorClassFeat> }')
    isAttackOptionFeat = S.Boolean(
            'ASK { $key a <http://goonmill.org/2009/statblock.n3#AttackOptionFeat> }')
    isSpecialActionFeat = S.Boolean(
            'ASK { $key a <http://goonmill.org/2009/statblock.n3#SpecialActionFeat> }')
    isRangedAttackFeat = S.Boolean(
            'ASK { $key a <http://goonmill.org/2009/statblock.n3#RangedAttackFeat> }')
    isSpeedFeat = S.Boolean(
            'ASK { $key a <http://goonmill.org/2009/statblock.n3#SpeedFeat> }')

    additional = S.Literal('SELECT ?a { $key p:additional ?a }')
    benefit = S.Literal('SELECT ?a { $key p:benefit ?a }')
    choiceText = S.Literal('SELECT ?a { $key p:choiceText ?a }')
    prerequisiteText = S.Literal('SELECT ?a { $key p:prerequisiteText ?a }')
    noFeatComment = S.Literal('SELECT ?a { $key p:noFeatCommen ?a }')


def needDatabase(f):
    """
    If the database is not loaded yet, load it
    """
    def inner(*a, **kw):
        if db is None:
            log.msg("Opening rdf database", system="rdfquery")
            openDatabase()
        return f(*a, **kw)
    return inner

@needDatabase
def allFamilies():
    return db.allFamilies()

@needDatabase
def allSpecialAC():
    return db.allSpecialAC()

@needDatabase
def allSpecialActions():
    return db.allSpecialActions()

@needDatabase
def allAuras():
    return db.allAuras()


class SRDTriplesDatabase(S.TriplesDatabase):
    def allFamilies(self):
        ret = {}
        for k in db.query("SELECT ?f { ?f a c:Family }"):
            k = k[0]
            family = Family(db=db, key=k)
            ret[family.label] = family

        return ret
                
    def allAuras(self):
        ret = {}
        for _a in db.query("SELECT ?a { ?a a c:Aura }"):
            a = _a[0]
            aura = Aura(db=db, key=a)
            ret[aura.label.lower()] = aura

        return ret

    def allSpecialAC(self):
        ret = {}
        for _ac in db.query("SELECT ?ac { ?ac a c:SpecialArmorClass }"):
            ac = _ac[0]
            armor = SpecialArmorClass(db=db, key=ac)
            ret[armor.label.lower()] = armor

        return ret

    def allSpecialActions(self):
        ret = {}
        for _sa in db.query("SELECT ?sa { ?sa a c:SpecialAction }"):
            sa = _sa[0]
            action = SpecialAction(db=db, key=sa)
            ret[action.label.lower()] = action

        return ret


db = None

def openDatabase():
    """
    Open the database. Has the side-effect of making the db available at the
    module level.
    """
    global db
    db = SRDTriplesDatabase()
    db.open(DB_LOCATION)

    return db


