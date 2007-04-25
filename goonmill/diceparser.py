from simpleparse import parser, dispatchprocessor as disp, objectgenerator
from simpleparse.common import numbers


grammar = r'''# RPG-STYLE DICE EXPRESSIONS
<ws> := [ \t]*
<n> := int
dieSize := 'd',ws,n
count := n
dieSet := count?,ws,dieSize
dieModifier := [+-],ws,n
repeat := n
rollRepeat := 'x',ws,repeat
staticNumber := n,ws,?-'d'
randomNumber := dieSet,ws,dieModifier?
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
        self.staticNumber = None

    def __repr__(self):
        if self.staticNumber is None:
            return '<DiceExpression %dd%d%+dx%d>' % (self.count, self.dieSize,
                    self.dieModifier, self.repeat)
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

    def count(self, (t,s1,s2,sub), buffer):
        self.expr.count = int(buffer[s1:s2])

    def dieModifier(self, (t,s1,s2,sub), buffer):
        self.expr.dieModifier = int(buffer[s1:s2])

    def dieSize(self, (t,s1,s2,sub), buffer):
        self.expr.dieSize = int(buffer[s1+1:s2])

    def repeat(self, (t,s1,s2,sub), buffer):
        self.expr.repeat = int(buffer[s1:s2])

    def rollRepeat(self, (t,s1,s2,sub), buffer):
        return disp.dispatch(self, sub[0], buffer)

diceParser = parser.Parser(grammar, root="diceExpressionRoot")

def parseDice(s):
    return diceParser.parse(s, processor=Processor())

diceExpression = objectgenerator.LibraryElement(
		generator = diceParser._generator,
		production = 'diceExpression',
        )

tests = [
    ' d10',
    ' 2d20',
    '2d20+1',
    '2d 20+1',
    '2 d 20- 1',
    '1d20 +1x5 2d20',
    '2',
    '2d',
]

if __name__ == '__main__':
    for test in tests:
        print test,
        suc, children, next = parseDice(test)
        assert suc and next==len(test)
        print children
