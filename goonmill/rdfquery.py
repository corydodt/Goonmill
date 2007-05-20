import os

from goonmill.util import RESOURCE
from goonmill import sparqly as S

from rdflib.Namespace import Namespace as NS

fam = NS('http://thesoftworld.com/2007/family.n3#')
char = NS('http://thesoftworld.com/2007/characteristic.n3#')
dice = NS('http://thesoftworld.com/2007/dice.n3#')
pcclass = NS('http://thesoftworld.com/2007/pcclass.n3#')

class Sense(S.SparqItem):
    label = S.Literal('SELECT ?l $datasets { $key c:label ?l }', default=S.Key(transform=S.iriToTitle))
    description = S.Literal('SELECT ?d $datasets { $key c:description ?d }')


class Family(S.SparqItem):
    senses = S.Ref(Sense, 'SELECT ?s $datasets { $key :traits [ :senses [ ?s [] ]]}')


def filenameAsUri(fn):
    return 'file://' + os.path.abspath(fn)


# create the root database for my triples-based SRD
prefixes = {'': str(fam), 'c': str(char) }

db = S.TriplesDatabase(
        str(fam),
        prefixes=prefixes,
        datasets=[filenameAsUri(RESOURCE('n3data/family.n3')),
             filenameAsUri(RESOURCE('n3data/characteristic.n3')),
             ],
        )

devil = Family(db=db, key=":devil")
senses = devil.senses
print senses[0].label

ooze = Family(db=db, key=":ooze")
senses = ooze.senses
print senses[0].label, senses[1].label
