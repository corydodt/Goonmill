"""
Parse saves in the form:

    Fort +1, Ref -, Will +2*

... etc.

"""

from parserbase import P, L, SL, W, number, splat, qualifier

undefined = L('-').setResultsName('undefined')

optQual = P.Optional(qualifier)
optSplat = P.Optional(splat)

fortSave = L('Fort') + (undefined ^ number)
fortSave = P.Group(fortSave + optSplat + optQual).setResultsName('fort')
refSave = L('Ref') + (undefined ^ number)
refSave = P.Group(refSave + optSplat + optQual).setResultsName('ref')
willSave = L('Will') + (undefined ^ number)
willSave = P.Group(willSave + optSplat + optQual).setResultsName('will')

# all three saves
saveList = P.delimitedList((fortSave | refSave | willSave)).setResultsName('saveList')

other = (P.NotAny(L('Fort')) + P.restOfLine).setResultsName('other')

# The big boy: anything allowed in the 'saves' attribute of a monster
saveStat = (other | saveList) + P.stringEnd

tests = ( # {{{
"""Fort +9, Ref +6, Will +8
Fort -9, Ref -, Will +8
Fort +9, Ref - , Will +8
Fort +9, Ref +1, Will -8
Fort +14 (+18 against poison), Ref +12, Will +12
Fort +9*, Ref +1*, Will -8*
As master's saves""".splitlines()) # }}}


if __name__ == '__main__': # {{{
    for slist in tests:
        print slist
        try:
            parsed = saveStat.parseString(slist)
        except Exception, e:
            raise##import sys, pdb; pdb.post_mortem(sys.exc_info()[2])
        print parsed
# }}}
