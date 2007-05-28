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
family := (l+, ws, c'traits')/(l+, ws, 'subtype')
immunity := ((c'immune to'/c'immunity to'),  ws, qWords)/((?-c'immunity', qWord, ws)+, c'immunity')
vulnerability := (c'vulnerability to', !, ws, qWords)/((?-c'vulnerability', qWord, ws)+, c'vulnerability')
resistance := (?-'resistance', qWord, ws)+, c'resistance', ws, n
darkvision := c'darkvision', !, range
blindSense := c'blindsense', !, range
blindSight := c'blindsight', !, range
telepathy := c'telepathy', !, range
tremorsense := c'tremorsense', !, range
lowLightVision := c'low-light vision'
allAroundVision := c'all-around vision'
seeInDarkness := c'see in darkness'
spells := c'spells (caster level ', n, l*, ')'
scent := c'scent'
keenSenses := c'keen senses'
alternateForm := c'alternate form'
waterBreathing := c'water breathing'
aura := (c'aura of', !, ws, (qWord, ws)+)/((?-c'aura', qWord, ws)+, 'aura')
empathy := (?-'empathy', qWord, ws)+, 'empathy'

# catcher for stuff like "immune to foo, bar, and zam"
illegalAnd := 'and', ws, !, 'DIE'

unknownQuality := (qualityChar/parenExpression)*

>quality< := illegalAnd/empathy/aura/waterBreathing/alternateForm/keenSenses/telepathy/tremorsense/scent/darkvision/blindSense/blindSight/lowLightVision/allAroundVision/seeInDarkness/damageReduction/regeneration/fastHealing/spells/family/immunity/vulnerability/resistance/unknownQuality

empty := '-'

specialQualityStat := empty/(quality, !, (sep, ws, quality)*)

specialQualityRoot := specialQualityStat
''') # }}}


specialQualityParser = parser.Parser(grammar, root='specialQualityRoot')


class Quality(object):
    count = 0
    unknowns = {}
    def __init__(self, type, text):
        Quality.count = Quality.count + 1
        self.type = type
        self.text = text
        if type == 'unknown':
            uq = Quality.unknowns.get(text)
            if uq is None:
                self.unknowns[text] = 1
            else:
                self.unknowns[text] = uq + 1


spellLikes = { # {{{
'move earth': 1,
'control water': 1,
'speak with animals': 1,
'fog cloud': 1,
'suggestion': 1,
'spider climb': 1,
'create/destroy water': 1,
'tongues': 1,
'plant growth': 1,
'control winds': 1,
'resilient sphere': 1,
'locate object': 1,
'feather fall': 1,
'darkness': 1,
'blur': 1,
'bless': 1,
'stone shape': 1,
'control weather': 1,
'wall of force': 1,
'ventriloquism': 1,
'sunbeam': 1,
'gust of wind': 1,
'create food and water': 1,
'transmute rock to mud/mud to rock': 1,
'sunburst': 1,
'hallucinatory terrain': 1,
'geas/quest': 1,
'forcecage': 1,
'teleport': 1,
'plane shift': 1,
'wall of stone': 1,
'prismatic wall': 1,
'find the path': 1,
'greater invisibility': 1,
'air walk': 1,
'blink': 1,
'detect good': 1,
'detect magic': 1,
'dimension door': 1,
'command undead': 1,
'cure serious wounds': 1,
'gaseous form': 1,
'haste': 1,
'invisibility': 1,
'mirage arcana': 1,
'prismatic sphere': 1,
'telekinetic sphere': 1,
'antimagic field': 1,
'dominate person': 1,
'etherealness': 1,
'insect plague': 1,
'maze': 1,
'veil': 1,
'wall of ice': 1,
'foresight': 1,
'endure elements': 1,
'magic circle against evil': 1,
'magic circle against good': 1,
'ethereal jaunt': 1,
'detect thoughts': 1,
'displacement': 1,
} # }}}


class Processor(disp.DispatchProcessor):
    def specialQualityStat(self, (t,s1,s2,sub), buffer):
        self.specialQualities = []
        disp.dispatchList(self, sub, buffer)
        return self.specialQualities

    def aura(self, (t,s1,s2,sub), buffer):
        q = Quality('aura', buffer[s1:s2])
        self.specialQualities.append(q)

    def waterBreathing(self, (t,s1,s2,sub), buffer):
        q = Quality('waterBreathing', buffer[s1:s2])
        self.specialQualities.append(q)

    def alternateForm(self, (t,s1,s2,sub), buffer):
        q = Quality('alternateForm', buffer[s1:s2])
        self.specialQualities.append(q)

    def keenSenses(self, (t,s1,s2,sub), buffer):
        q = Quality('keenSenses', buffer[s1:s2])
        self.specialQualities.append(q)

    def tremorsense(self, (t,s1,s2,sub), buffer):
        q = Quality('tremorsense', buffer[s1:s2])
        self.specialQualities.append(q)

    def telepathy(self, (t,s1,s2,sub), buffer):
        q = Quality('telepathy', buffer[s1:s2])
        self.specialQualities.append(q)

    def scent(self, (t,s1,s2,sub), buffer):
        q = Quality('scent', buffer[s1:s2])
        self.specialQualities.append(q)

    def spells(self, (t,s1,s2,sub), buffer):
        q = Quality('spells', buffer[s1:s2])
        self.specialQualities.append(q)

    def blindSense(self, (t,s1,s2,sub), buffer):
        q = Quality('blindSense', buffer[s1:s2])
        self.specialQualities.append(q)

    def blindSight(self, (t,s1,s2,sub), buffer):
        q = Quality('blindSight', buffer[s1:s2])
        self.specialQualities.append(q)

    def darkvision(self, (t,s1,s2,sub), buffer):
        q = Quality('darkvision', buffer[s1:s2])
        self.specialQualities.append(q)

    def allAroundVision(self, (t,s1,s2,sub), buffer):
        q = Quality('allAroundVision', buffer[s1:s2])
        self.specialQualities.append(q)

    def seeInDarkness(self, (t,s1,s2,sub), buffer):
        q = Quality('seeInDarkness', buffer[s1:s2])
        self.specialQualities.append(q)

    def lowLightVision(self, (t,s1,s2,sub), buffer):
        q = Quality('lowLightVision', buffer[s1:s2])
        self.specialQualities.append(q)

    def vulnerability(self, (t,s1,s2,sub), buffer):
        q = Quality('vulnerability', buffer[s1:s2])
        self.specialQualities.append(q)

    def immunity(self, (t,s1,s2,sub), buffer):
        newQualities = []
        buf = buffer[s1:s2]
        if ' and ' in buf:
            assert buf.startswith('immunity')
            imms = buf[len('immunity to'):].split(' and ')
            for imm in imms:
                q = Quality('immunity', imm.strip())
                newQualities.append(q)
        else:
            q = Quality('immunity', buffer[s1:s2])
            newQualities = [q]
        self.specialQualities.extend(newQualities)

    def resistance(self, (t,s1,s2,sub), buffer):
        q = Quality('resistance', buffer[s1:s2])
        self.specialQualities.append(q)

    def regeneration(self, (t,s1,s2,sub), buffer):
        q = Quality('regeneration', buffer[s1:s2])
        self.specialQualities.append(q)

    def damageReduction(self, (t,s1,s2,sub), buffer):
        q = Quality('damageReduction', buffer[s1:s2])
        self.specialQualities.append(q)

    def fastHealing(self, (t,s1,s2,sub), buffer):
        q = Quality('fastHealing', buffer[s1:s2])
        self.specialQualities.append(q)

    def empathy(self, (t,s1,s2,sub), buffer):
        q = Quality('empathy', buffer[s1:s2])
        self.specialQualities.append(q)

    def family(self, (t,s1,s2,sub), buffer):
        q = Quality('family', buffer[s1:s2])
        self.specialQualities.append(q)

    def empty(self, (t,s1,s2,sub), buffer):
        pass

    def unknownQuality(self, (t,s1,s2,sub), buffer):
        s = buffer[s1:s2]
        if s.lower() in spellLikes:
            q = Quality('spellLike', s)
            self.specialQualities.append(q)
        else:
            q = Quality('unknown', buffer[s1:s2])
            self.specialQualities.append(q)


def parseSpecialQualities(s):
    succ, children, end = attackParser.parse(s, processor=Processor())
    if not succ or not end == len(s):
        raise RuntimeError('%s is not a valid attack expression' % (s,))
    return children


def printFrequenciesOfUnknowns():
    items = Quality.unknowns.items()
    for n, (k, freq) in enumerate(items):
        items[n] = freq, k
    import pprint
    pprint.pprint(sorted(items))
    print sum(zip(*items)[0]), "total unknowns"
    print Quality.count, "total qualities parsed"


if __name__ == '__main__': # {{{
    tests = query._allSQStats()
    for id, test in tests:
        #print id, test
        suc, children, next = specialQualityParser.parse(test, processor=Processor())
        #print children
        assert next==len(test),  test[:next] + '\n--\n' + test[next:]

    printFrequenciesOfUnknowns()
# }}}
