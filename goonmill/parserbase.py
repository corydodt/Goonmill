"""
Base stuff that will be reused for all pyparsing parsers in Goonmill
"""
import string

import pyparsing as P

L = P.Literal
SL = lambda c: P.Suppress(L(c))
W = P.Word

# the noble number
numberChars = P.nums # + ','
numberBase = W(numberChars, min=1)
number = P.Combine(P.Optional(P.oneOf('+ -')) + P.Optional(P.White()) +
        numberBase).setResultsName('number')

def convertNumber(s,p,t):
    return int(t[0].replace(',', ''))

number.setParseAction(convertNumber)



# (an empty list)
emptyList = L('-').setResultsName('emptyList')
emptyList.setParseAction(lambda s,p,t: 'empty')


namePrintables = ''.join([c for c in P.printables if c not in ',()-+'])
nameWord = W(namePrintables)

splat = L('*').setResultsName('splat')


# a qualifier could be just about anything..
qualifierChars = namePrintables + '-+' + string.whitespace

inParenQualifierChars = qualifierChars + ','
inParenQualifier = P.Combine(P.OneOrMore(W(inParenQualifierChars), ' '))
parenQualifier = SL('(') + inParenQualifier + SL(')')

qualifier = P.Combine(P.OneOrMore(parenQualifier)).setResultsName('qualifier')
