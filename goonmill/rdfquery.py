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


class SpecialAbility(S.SparqItem):
    """A notable ability of any kind that isn't a standard combat mechanic"""


class Family(S.SparqItem):
    """A family of monster with shared characteristics"""
    senses = S.Ref(Sense, 
        'SELECT ?s { $key :traits [ :senses [ ?s [] ]]}')
    specialAbilities = S.Ref(SpecialAbility, 
        'SELECT ?spec { ?spec a c:SpecialAbility . $key :traits [ ?spec [] ] }')


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

template = '''%s
Senses: %s
Special Abilities
-----------------
'''

specs = '''%s
 %s
'''

def formatFamily(key):
    family = Family(db=db, key=key)
    senses = ' '.join([s.label for s in family.senses])
    print template % (family.label, senses)
    for s in family.specialAbilities:
        print specs % (s.label, s.comment)

formatFamily(fam.devil)
formatFamily(fam.ooze)
