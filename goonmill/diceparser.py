"""
Parser for robust dice expressions.
"""
import sys

import pyparsing as P

L = P.Literal
CL = P.CaselessLiteral
Sup = P.Suppress


# dice expressions
# general format:
#
#    number ::== {'0'-'9'}...
#    filter ::= { 'h' | 'l' } number
#    bonus ::=  { '+' | '-'} number
#    repeat ::= 'x' number
#    size ::== 'd' number
#    random ::= [ number ] size [ filter ] [ bonus ] [ repeat ]
#    nonrandom ::= number [ bonus ] [ repeat ]
#    
number = P.Word((P.nums + ','))
number.setParseAction(lambda s,p,t: map(int, [_t.replace(',','') for _t in t]))

dice_count = number.setResultsName('dice_count')
dice_size = Sup(CL('d')) + number.setResultsName('dice_size')
dice_bonus = P.oneOf('+ -') + number.setResultsName('dice_bonus')
dice_filter = (P.oneOf('h l', caseless=True).setResultsName('dice_hilo') +
               number.setResultsName('dice_filter'))
dice_sorted = CL('sort').setResultsName('dice_sorted')
dice_repeat = (Sup(CL('x')) + 
               number.setResultsName('dice_repeat') + 
               P.Optional(dice_sorted))

def combineBonus(sign, num):
    values = {'-':-1, '+':1}
    return num * values[sign]

class FilterException(Exception):
    """Filter has more dice than the dice_count"""

dice_bonus.setParseAction(lambda s, p, t: combineBonus(*t))
dice_bonus = dice_bonus.setResultsName('dice_bonus')

dice_optionals = P.Optional(dice_bonus) + P.Optional(dice_repeat)

nonrandom = (dice_count + dice_optionals)
random = (P.Optional(dice_count, default=1) + 
          dice_size +
          P.Optional(dice_filter) + 
          dice_optionals)

dice = (random | nonrandom).setResultsName('DICE')
dice_string = dice + P.StringEnd()

def reverseFormatDice(parsed_dice):
    """Take a parsed dice expression and return the string form"""
    _dice_expr = []
    if parsed_dice.dice_count:
        _dice_expr.append(str(parsed_dice.dice_count))
    if parsed_dice.dice_size:
        _dice_expr.append('d' + str(parsed_dice.dice_size))
    if parsed_dice.dice_hilo:
        _dice_expr.append(str(parsed_dice.dice_hilo[0]))
    if parsed_dice.dice_filter:
        _dice_expr.append(str(parsed_dice.dice_filter))
    if parsed_dice.dice_bonus:
        _dice_expr.append('%+d' % (parsed_dice.dice_bonus,))
    if parsed_dice.dice_repeat:
        _dice_expr.append('x' + str(parsed_dice.dice_repeat))
    if parsed_dice.dice_sorted:
        _dice_expr.append('sort')
    return ''.join(_dice_expr)

_test_dice = [("5", "[5]"), # {{{
("5x3","[5, 3]"),
("5+1x3","[5, 1, 3]"),
("d6x3","[1, 6, 3]"),
("1d20+1","[1, 20, 1]"),
("9d6l3-10x2","[9, 6, 'l', 3, -10, 2]"),
("9d6H3+10x2","[9, 6, 'h', 3, 10, 2]"),
("1d  6 X3","[1, 6, 3]"),
("d 6 -2 x 3","[1, 6, -2, 3]"),
("2d6-2x1","[2, 6, -2, 1]"),
("2d6-2x2sort","[2, 6, -2, 2, 'sort']"),
("100d2+1,243","[100, 2, 1243]"),
("2d6sort", P.ParseException),
("d6xz", P.ParseException),
("1d", P.ParseException),
("1d6l3l3", P.ParseException),
("1d6h3l3", P.ParseException),
("d6h+1", P.ParseException),
] # }}}


def passed():
    global passcount
    passcount = passcount + 1
    sys.stdout.write('.')

def testStuff(method, tests):
    for input, expected in tests:
        try:
            parsed = method(input)
            if isinstance(expected, basestring):
                if str(parsed) != expected:
                    print '\n', input, 'Wanted', expected, 'Got', str(parsed)
                else:
                    passed()
            else:
                print "\nFAILED:", input, 'Wanted', expected, 'Got', parsed
        except Exception, e:
            if isinstance(expected, basestring):
                print "\nFAILED:", input, expected
                raise
            if not isinstance(e, expected):
                print input, expected, str(parsed)
            else:
                passed()

passcount = 0

def test():
    testStuff(dice_string.parseString, _test_dice)
    print passcount

if __name__ == '__main__':
    test()
