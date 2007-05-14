"""
Parse special qualities, special attacks, all that shit.

There's an Australian fuck-ton (10% bigger than the English fuck-ton) of weird
shit that can happen in here, so basically split on commas and look for things
I understand, and whack anything else into an Unknown object.

"""
from simpleparse import parser, dispatchprocessor as disp
from simpleparse.common import chartypes, numbers

from goonmill import query

grammar = ( # {{{
r'''# special quality stat
<wsc> := [ \t]
<ws> := wsc*
<n> := int
<l> := letter
<d> := digit
<paren> := [()]

<qualityChar> := l/d/wsc/[-/+.']

<qWord> := (l/d/[-/+.'])+
<qWords> := (qWord, ws?)+

<sep> := [,;]

<parenExpression> := '(', !, (qualityChar/',')*, ')'

<range> := ws, n, ws, 'ft.'


# here we go with a whole buttload of specific elements
damageReduction := c'damage reduction', !, ws, n, '/', (qWord, ws?)+
regeneration := c'regeneration', !, ws, n
fastHealing := c'fast healing', !, ws, n
family := l+, ws, c'traits'
immunity := ((c'immune to'/c'immunity to'),  ws, qWords)/((?-c'immunity', qWord, ws)+, c'immunity')
vulnerability := (c'vulnerability to', !, ws, qWords)/((?-c'vulnerability', qWord, ws)+, c'vulnerability')
resistance := (?-'resistance', qWord, ws)+, c'resistance', ws, n
darkvision := c'darkvision', !, range
blindSense := c'blindsense', !, range
blindSight := c'blindsight', !, range
telepathy := c'telepathy', !, range
tremorsense := c'tremorsense', !, range
lowLightVision := c'low-light vision'
spells := c'spells (caster level ', n, l+, ')'
scent := c'scent'
keenSenses := c'keen senses'

# catcher for stuff like "immune to foo, bar, and zam"
illegalAnd := 'and', ws, !, 'DIE'

unknownQuality := (qualityChar/parenExpression)*

>quality< := illegalAnd/keenSenses/telepathy/tremorsense/scent/darkvision/blindSense/blindSight/lowLightVision/damageReduction/regeneration/fastHealing/spells/family/immunity/vulnerability/resistance/unknownQuality

empty := '-'

specialQualityStat := empty/(quality, !, (sep, ws, quality)*)

specialQualityRoot := specialQualityStat
''') # }}}

specialQualityParser = parser.Parser(grammar, root='specialQualityRoot')


class Quality(object):
    def __repr__(self):
        if self.repr:
            return self.repr
        return super(Quality, self).__repr__()


class UnknownQuality(Quality):
    def __repr__(self):
        return '<UQ %s>' % (self.s,)

class KeenSenses(Quality):
    repr = "KS"

class Telepathy(Quality):
    repr = "T"

class BlindSight(Quality):
    repr = "BSi"

class BlindSense(Quality):
    repr = "BS"

class Immunity(Quality):
    repr = "I"

class Resistance(Quality):
    repr = "R"

class FastHealing(Quality):
    repr = "FH"

class DamageReduction(Quality):
    repr = "DR"

class Regeneration(Quality):
    repr = "Rg"

class Family(Quality):
    repr = "F"

class Vulnerability(Quality):
    repr = "V"

class Darkvision(Quality):
    repr = "DV"

class Spells(Quality):
    repr = "S"

class Scent(Quality):
    repr = "Sc"

class Tremorsense(Quality):
    repr = "Tm"

class LowLightVision(Quality):
    repr = "LLV"


class Processor(disp.DispatchProcessor):
    def specialQualityStat(self, (t,s1,s2,sub), buffer):
        self.specialQualities = []
        disp.dispatchList(self, sub, buffer)
        return self.specialQualities

    def keenSenses(self, (t,s1,s2,sub), buffer):
        q = KeenSenses()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def tremorsense(self, (t,s1,s2,sub), buffer):
        q = Tremorsense()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def telepathy(self, (t,s1,s2,sub), buffer):
        q = Telepathy()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def scent(self, (t,s1,s2,sub), buffer):
        q = Scent()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def spells(self, (t,s1,s2,sub), buffer):
        q = Spells()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def blindSense(self, (t,s1,s2,sub), buffer):
        q = BlindSense()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def blindSight(self, (t,s1,s2,sub), buffer):
        q = BlindSight()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def darkvision(self, (t,s1,s2,sub), buffer):
        q = Darkvision()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def lowLightVision(self, (t,s1,s2,sub), buffer):
        q = LowLightVision()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def vulnerability(self, (t,s1,s2,sub), buffer):
        q = Vulnerability()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def immunity(self, (t,s1,s2,sub), buffer):
        q = Immunity()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def resistance(self, (t,s1,s2,sub), buffer):
        q = Resistance()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def regeneration(self, (t,s1,s2,sub), buffer):
        q = Regeneration()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def damageReduction(self, (t,s1,s2,sub), buffer):
        q = DamageReduction()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def fastHealing(self, (t,s1,s2,sub), buffer):
        q = FastHealing()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def family(self, (t,s1,s2,sub), buffer):
        q = Family()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)

    def empty(self, (t,s1,s2,sub), buffer):
        pass

    def unknownQuality(self, (t,s1,s2,sub), buffer):
        q = UnknownQuality()
        q.s = buffer[s1:s2]
        self.specialQualities.append(q)


def parseSpecialQualities(s):
    succ, children, end = attackParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid attack expression' % (s,))
    return children


if __name__ == '__main__': # {{{
    tests = query._allSQStats()
    for id, test in tests:
        #print id, test
        suc, children, next = specialQualityParser.parse(test, processor=Processor())
        print children
        assert next==len(test),  test[:next] + '\n--\n' + test[next:]
# }}}
