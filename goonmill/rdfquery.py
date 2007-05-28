import os

from goonmill.util import RESOURCE
from goonmill import sparqly as S

from rdflib.Namespace import Namespace as NS

fam = NS('http://thesoftworld.com/2007/family.n3#')
char = NS('http://thesoftworld.com/2007/characteristic.n3#')
dice = NS('http://thesoftworld.com/2007/dice.n3#')
pcclass = NS('http://thesoftworld.com/2007/pcclass.n3#')
prop = NS('http://thesoftworld.com/2007/properties.n3#')

class Sense(S.SparqItem):
    """A notable sense possessed by monsters, such as darkvision"""


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



def filenameAsUri(fn):
    return 'file://' + os.path.abspath(fn)


# create the root database for my triples-based SRD
prefixes = {'': fam, 'c': char, 'p': prop}


def allFamilies():
    return db.allFamilies()


class SRDTriplesDatabase(S.TriplesDatabase):
    def allFamilies(self):
        ret = {}
        for k in db.query("SELECT ?f { ?f a c:Family }"):
            k = k[0]
            family = Family(db=db, key=k)
            ret[family.label] = family

        return ret
                


db = SRDTriplesDatabase(
        str(fam),
        prefixes=prefixes,
        datasets=[filenameAsUri(RESOURCE('n3data/family.n3')),
                  filenameAsUri(RESOURCE('n3data/characteristic.n3')),
                  ],
        )

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
# }}}
