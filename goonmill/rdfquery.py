from playtools import sparqly as S

from rdflib.Namespace import Namespace as NS

fam = NS('http://thesoftworld.com/2007/family.n3#')
char = NS('http://thesoftworld.com/2007/characteristic.n3#')
dice = NS('http://thesoftworld.com/2007/dice.n3#')
pcclass = NS('http://thesoftworld.com/2007/pcclass.n3#')
prop = NS('http://thesoftworld.com/2007/property.n3#')

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


def allFamilies():
    return db.allFamilies()

def allSpecialAC():
    return db.allSpecialAC()

def allSpecialActions():
    return db.allSpecialActions()

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


from goonmill.util import RESOURCE as R2
db = SRDTriplesDatabase(**S.bootstrapDatabaseConfig(R2('tripledb.n3')))


if __name__ == '__main__': # {{{
    import string
    template = string.Template('''$name
    Senses: $senses
    Languages: $languages
    Special Abilities
    -----------------
    $specs
    Special Qualities
    -----------------
    $specQ
    Combat Mechanics
    ----------------
    $combatMech
    ''')

    specs = string.Template('''$specLabel
      $specComment
    ''')

    from twisted.python import text
    def formatComment(c):
        return '\n      '.join(text.greedyWrap(c))

    def formatFamily(key):
        fam = Family(db=db, key=key)

        senses = ', '.join([sen.label for sen in fam.senses])
        languages = ', '.join([l.label for l in fam.languages])
        abilities = []
        for spec in fam.specialAbilities:
            abilities.append(specs.substitute(specLabel='- ' + spec.label, 
                specComment=formatComment(spec.comment)))
        abilities = ''.join(abilities)

        qualities = []
        for spec in fam.specialQualities:
            qualities.append(specs.substitute(specLabel='- ' + spec.label, 
                specComment=formatComment(spec.comment)))
        qualities= ''.join(qualities)

        combatMechanics = []
        for spec in fam.combatMechanics:
            combatMechanics.append(specs.substitute(specLabel='- ' + spec.label, 
                specComment=formatComment(spec.comment)))
        combatMechanics= ''.join(combatMechanics)

        print template.substitute(name=fam.label, 
                senses=senses, 
                languages=languages, 
                specs=abilities,
                specQ=qualities,
                combatMech=combatMechanics)
        #


    formatFamily(fam.devil)
    formatFamily(fam.ooze)
    formatFamily(fam.undead)
    formatFamily(fam.construct)
    formatFamily(fam.fey)
# }}}
