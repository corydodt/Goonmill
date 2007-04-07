"""
Parse skills in the form
Foo +1, Bar +2*, Knowledge (arcana, history) -8
... etc.

"""
import string

import pyparsing as P

L = P.Literal
CL = P.CaselessLiteral
Sup = P.Suppress
SL = lambda c: Sup(L(c))
W = P.Word

# the noble number
numberChars = P.nums + ','
number = P.Combine(P.Optional(P.oneOf('+ -')) + P.Optional(P.White()) + W(numberChars)).setResultsName('number')

def convertNumber(s,p,t):
    return int(t[0].replace(',', ''))

number.setParseAction(convertNumber)


# skillName
skillNamePrintables = ''.join([c for c in P.printables if c not in ',()-+'])
skillNameWord = W(skillNamePrintables)

skillName = P.Group(P.OneOrMore(skillNameWord)).setResultsName('skillName')

def joinSkill(s,p,t):
    return ' '.join(t[0].asList())

skillName.setParseAction(joinSkill)




# subskills
subSkillGroup = P.Group(
        SL('(') + P.delimitedList(P.OneOrMore(skillName)) + SL(')')
        ).setResultsName('subSkillGroup')


# a qualifier could be just about anything..
qualifierChars = skillNamePrintables + '-+' + string.whitespace
orQualifier = P.Combine(L('or ') + W(qualifierChars))

inParenQualifierChars = qualifierChars + ','
inParenQualifier = P.Combine(P.OneOrMore(W(inParenQualifierChars), ' '))
parenQualifier = SL('(') + inParenQualifier + SL(')')

qualifier = P.Combine(P.OneOrMore(parenQualifier | orQualifier)).setResultsName('qualifier')

splat = L('*').setResultsName('splat')

# one whole skill
skill = P.Group(skillName + P.Optional(subSkillGroup) + number + P.Optional(splat) + P.Optional(qualifier) + P.Optional(splat)).setResultsName('skill')

# fucking Speak Language
languageName = L('Speak Language').setResultsName('languageName')
language = P.Group(languageName + P.Optional(subSkillGroup)).setResultsName('language')

# all the skills that a skill-having monster has
languageOrSkill = (language | skill)
skillList = P.delimitedList(P.OneOrMore(languageOrSkill)).setResultsName('skillList')

# (an empty skill list)
noSkillList = L('-').setResultsName('noSkillList')
noSkillList.setParseAction(lambda s,p,t: 'empty')



# The big boy: anything allowed in the 'skills' attribute of a monster
skillStat = (noSkillList | skillList) + P.stringEnd




tests = ( # {{{
"""-
Speak Language (elven, common)
Speak Language (any five), Jump +16*
Concentration -6, Hide +7, Move Silently +5, Psicraft +7, Ride +5, Spot +3
Knowledge (psionics) +12, Jump +1
Hide +15, Move Silently +7, Listen +6, Spot +2
Hide +1,000, Listen +5, Spot +5
Hide +9, Intimidate +12, Knowledge (psionics) +12, Listen +14, Psicraft +12, Search +12, Sense Motive +12, Spot +14* (comma, comma, ninjas)
Concentration +17, Hide +7, Jump +16, Knowledge (arcana) +12, Knowledge (psionics) +12, Knowledge (the planes) +12, Listen +22, Move Silently +11, Psicraft +12, Search +12, Sense Motive +14, Spot +22
Concentration +14, Diplomacy +17, Jump +0, Knowledge (any two) +15, Listen +16, Search +15, Sense Motive +16, Spellcraft +15 (+17 scrolls), Spot +16, Survival +4 (+6 following tracks), Tumble +15, Use Magic Device +15 (+17 scrolls)
Appraise +9, Climb +5, Jump +5, Listen +2, Spot +10
Climb +3, Jump +3
Listen +6, Move Silently +4, Spot +6
Spot +1
Bluff + 15, Concentration +11 (+15 when manifesting defensively), Hide +14, Listen +14, Move Silently +16
Jump +16 or as controlling spirit
Climb +38, Knowledge (psionics, arcane) +31, Listen +30, Psicraft +31, Spot +30
Climb +38 (+39 on a good day)*
Listen +11, Move Silently +7, Spot +11
Climb +14*, Listen +6, Move Silently +6, Search +2, Spot +6
Hide +22, Listen +7, Sense Motive +7, Spot +7
Climb +12, Jump +20, Listen +7, Spot +8
Listen +10
Bluff +10*, Diplomacy +6, Disguise +10*, Intimidate +6, Listen +6, Sense Motive +6, Spot +6
Climb +2, Jump +2
""".splitlines()) # }}}

if __name__ == '__main__':
    for slist in tests:
        print slist
        parsed = skillStat.parseString(slist)
        print parsed
