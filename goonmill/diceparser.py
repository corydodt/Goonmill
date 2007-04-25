from simpleparse import parser, dispatchprocessor as disp, objectgenerator
from simpleparse.common import numbers


grammar = r'''# RPG-STYLE DICE EXPRESSIONS
<ws> := [ \t]*
<n> := int

dieSize := 'd',ws,n
count := n
dieSet := count?,ws,dieSize

filter := [hHlL], n

dieModifier := [+-],ws,n

repeat := n
sorted := 'sort'
rollRepeat := 'x',ws,repeat,ws,sorted?

randomNumber := dieSet,ws,filter?,dieModifier?
staticNumber := n,ws,?-'d'

diceExpression := (staticNumber/randomNumber),ws,rollRepeat?

# normally my root production will not get called in the Processor,
# so define a dummy root around it, and then it will
diceExpressionRoot := (ws,diceExpression)+
'''

class DiceExpression(object):
    def __init__(self):
        self.count = 1
        self.dieSize = 1
        self.dieModifier = 0
        self.repeat = 1
        self.sort = ''
        self.filterDirection = 'h'
        self.filterCount = None
        self.staticNumber = None

    def __repr__(self):
        if self.staticNumber is None:
            filter = ''
            if self.filterCount is not None:
                filter = '%s%d' % (self.filterDirection, self.filterCount)

            return '<DiceExpression %dd%d%s%+dx%d%s>' % (self.count, self.dieSize,
                    filter, self.dieModifier, self.repeat, self.sort)
        return '<DiceExpression %d (static)>' % (self.staticNumber,)

class Processor(disp.DispatchProcessor):
    def diceExpression(self, (t,s1,s2,sub), buffer):
        self.expr = DiceExpression()
        disp.dispatchList(self, sub, buffer)
        return self.expr

    def randomNumber(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def staticNumber(self, (t,s1,s2,sub), buffer):
        self.expr.staticNumber = int(buffer[s1:s2])

    def dieSet(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def sorted(self, (t,s1,s2,sub), buffer):
        self.expr.sort = 'sort'

    def filter(self, (t,s1,s2,sub), buffer):
        self.expr.filterDirection = buffer[s1].lower()
        self.expr.filterCount = int(buffer[s1+1:s2])

    def count(self, (t,s1,s2,sub), buffer):
        self.expr.count = int(buffer[s1:s2])

    def dieModifier(self, (t,s1,s2,sub), buffer):
        self.expr.dieModifier = int(buffer[s1:s2])

    def dieSize(self, (t,s1,s2,sub), buffer):
        self.expr.dieSize = int(buffer[s1+1:s2])

    def repeat(self, (t,s1,s2,sub), buffer):
        self.expr.repeat = int(buffer[s1:s2])

    def rollRepeat(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

diceParser = parser.Parser(grammar, root="diceExpressionRoot")

def parseDice(s):
    return diceParser.parse(s, processor=Processor())

diceExpression = objectgenerator.LibraryElement(
		generator = diceParser._generator,
		production = 'diceExpression',
        )

tests = [ # {{{
    ' d10',
    ' 2d20',
    '2d20+1',
    '2d 20+1',
    '2 d 20- 1',
    '1d20 +1x5 2d20',
    "2d6-2x2sort",
    "9d6l3-10x2",
    "9d6H3+10x2",
    '2',
    '2d',
] # }}}


if __name__ == '__main__':
    for test in tests:
        print test,
        suc, children, next = parseDice(test)
        assert suc and next==len(test)
        print children
