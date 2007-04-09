"""
Base stuff that will be reused for all pyparsing parsers in Goonmill
"""

import pyparsing as P

L = P.Literal
SL = lambda c: P.Suppress(L(c))
W = P.Word

# the noble number
numberChars = P.nums + ','
number = P.Combine(P.Optional(P.oneOf('+ -')) + P.Optional(P.White()) + W(numberChars)).setResultsName('number')

def convertNumber(s,p,t):
    return int(t[0].replace(',', ''))

number.setParseAction(convertNumber)

# (an empty list)
emptyList = L('-').setResultsName('emptyList')
emptyList.setParseAction(lambda s,p,t: 'empty')


namePrintables = ''.join([c for c in P.printables if c not in ',()-+'])
nameWord = W(namePrintables)
