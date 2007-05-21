import os

from goonmill.util import RESOURCE
from goonmill import sparqly as S

from rdflib.Namespace import Namespace as NS

fam = NS('http://thesoftworld.com/2007/family.n3#')
char = NS('http://thesoftworld.com/2007/characteristic.n3#')
dice = NS('http://thesoftworld.com/2007/dice.n3#')
pcclass = NS('http://thesoftworld.com/2007/pcclass.n3#')

class Sense(S.SparqItem):
    """A notable sense possessed by monsters, such as darkvision"""


class Language(S.SparqItem):
    """A language understood by monsters"""


class SpecialAbility(S.SparqItem):
    """A notable ability of any kind that isn't a standard combat mechanic"""


class Family(S.SparqItem):
    """A family of monster with shared characteristics"""
    senses = S.Ref(Sense, 
        'SELECT ?s { $key :traits [ :senses [ ?s [] ]]}')
    specialAbilities = S.Ref(SpecialAbility, 
        'SELECT ?spec { ?spec a c:SpecialAbility . $key :traits [ ?spec [] ] }')
    languages = S.Ref(Language,
        'SELECT ?lng { ?lng a c:Language . $key :traits [ :languages ?lng ] }')


def filenameAsUri(fn):
    return 'file://' + os.path.abspath(fn)


# create the root database for my triples-based SRD
prefixes = {'': fam, 'c': char}

db = S.TriplesDatabase(
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
    ''')

    specs = string.Template('''$specLabel
     $specComment
    ''')

    def formatFamily(key):
        fam = Family(db=db, key=key)

        senses = ', '.join([sen.label for sen in fam.senses])
        languages = ', '.join([l.label for l in fam.languages])
        abilities = []
        for spec in fam.specialAbilities:
            abilities.append(specs.substitute(specLabel=spec.label, 
                specComment=spec.comment))
        abilities = ''.join(abilities)

        print template.substitute(name=fam.label, senses=senses, languages=languages, specs=abilities)
        #


    formatFamily(fam.devil)
    formatFamily(fam.ooze)
# }}}
