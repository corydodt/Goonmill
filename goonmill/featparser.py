"""
Parse feats in the form:

    Foo, Weapon Specialization (katana, club), Improved Sunder

... etc.

"""
import string

from parserbase import P, L, SL, W, number, emptyList, namePrintables, nameWord


# featName
featNamePrintables = namePrintables + '-'
featNameWord = W(featNamePrintables)
featName = P.Group(P.OneOrMore(featNameWord)).setResultsName('featName')

def joinFeat(s,p,t):
    return ' '.join(t[0].asList())

featName.setParseAction(joinFeat)


# subfeats 
subFeatGroup = P.Group(
        SL('(') + P.delimitedList(P.OneOrMore(featName)) + SL(')')
        ).setResultsName('subFeatGroup')


# one whole feat
feat = P.Group(featName + P.Optional(subFeatGroup)).setResultsName('feat')


# all the feats a feat-having monster has
featList = P.delimitedList(P.OneOrMore(feat)).setResultsName('featList')


# lycanthropes have this literal text, so check for it
lycanthrope = P.Group(P.Combine(L('(same as ') + 
    P.OneOrMore(nameWord) + L(' form)'))).setResultsName('lycanthrope')


# The big boy: anything allowed in the 'skills' attribute of a monster
featStat = (emptyList | lycanthrope | featList) + P.stringEnd



tests = ( # {{{
"""-
Ability Focus (poison), Alertness, Flyby Attack
Iron Will, Toughness (2)
Alertness, Empower Spell, Flyby Attack, Hover, Improved Initiative, Maximize Spell, Power Attack, Weapon Focus (bite), Weapon Focus (claw), Wingover
Alertness, Improved Critical (chain), Improved Initiative
Multiattack, Toughness
Cleave, Improved Sunder, Iron Will, Multiattack, Power Attack, Weapon Focus (spiked chain)
Alertness, Iron Will, Track
Blind-Fight, Cleave, Combat Reflexes, Improved Initiative, Power Attack
Great Fortitude, Ride-by Attack, Spirited Charge
Alertness, Combat Reflexes, Improved Initiative, Skill Focus (Sense Motive), Skill Focus (Survival), Stealthy, Track
Alertness, Toughness
Weapon Focus (rapier)
Alertness
Alertness, Diehard, Endurance, Toughness (2)
Flyby Attack, Improved Initiative, Improved Critical (bite), Iron Will, Multiattack, Weapon Focus (eye ray), Weapon Focus (bite)
Alertness, Empower Spell, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Alertness, Hover, Improved Initiative, Weapon Focus (bite)
Alertness, Weapon Focus (morningstar)
Alertness, Empower Spell, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
Alertness, Awesome Blow, Blind-Fight, Cleave, Combat Reflexes, Dodge, Great Cleave, Improved Bull Rush, Improved Initiative, Iron Will, Power Attack, Toughness (6)
Weapon Focus (longbow), item creation feat (any one)
Alertness, Blind-Fight, Cleave, Empower Spell, Flyby Attack, Hover, Improved Initiative, Maximize Spell, Power Attack, Snatch, Weapon Focus (bite), Weapon Focus (claw), Wingover
Alertness, Empower Spell, Flyby Attack, Hover, Improved Initiative, Power Attack, Weapon Focus (bite), Weapon Focus (claw)
(same as human form)
""".splitlines()) # }}}

if __name__ == '__main__':
    for flist in tests:
        print flist
        parsed = featStat.parseString(flist)
        print parsed
