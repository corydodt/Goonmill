from goonmill import diceparser, query

from simpleparse import parser, dispatchprocessor as disp, error
from simpleparse.common import numbers, chartypes

grammar = r'''# RPG-STYLE DICE EXPRESSIONS
<wsc> := [ \t]
<ws> := wsc*
<n> := int
<l> := letter
<d> := digit
<paren> := [()]
splat := '*'

count := n

<weaponChar> := l/d/wsc/paren
<nonTerminalDash> := ('-', l)
weapon := (weaponChar/nonTerminalDash)+

bonus := [-+], n
bonusSequence := bonus, ('/', bonus)*

cwb := count?, ws, weapon, ws, bonusSequence

attackTypeSlot := ('melee'/'ranged'), splat?
attackTouchSlot := 'touch'
attackTypeAndTouch := attackTypeSlot, ws, attackTouchSlot?

critRange := n, '-', n
critThreat := 'x', n
crit := (critRange, '/', critThreat)/critRange/critThreat

extraDamage := (l/d/wsc/[,+-])+
<damageType> := (l/d/wsc/'+')+
damage := diceExpression?, ws, damageType?, splat?
parenDamage := '(', extraDamage, ')'
extraClause := (parenDamage/extraDamage)*, ws
damageSet := damage, ('/', crit)?
damagePhrase := '(', damageSet, (',', damageSet)*, ws, extraClause?, ws, ')'

<rangeInformation> := (l/d/wsc/[.+-])+
rangeSlot := '(', rangeInformation, ')'

# two choices
subAttackForm1 := damagePhrase, ws, attackTypeAndTouch
subAttackForm2 := attackTypeAndTouch, ws, damagePhrase

anyAttackForm := cwb, ws, !, subAttackForm1/subAttackForm2, ws, rangeSlot?

<attackFormSep> := ','/'and'

attackOption := anyAttackForm, (attackFormSep, ws, anyAttackForm)*

empty := '-'

attackStat := empty/(attackOption, (';'?, ws, 'or', ws, attackOption)*)

attackStatRoot := attackStat
'''

attackParser = parser.Parser(grammar, root='attackStatRoot', prebuilts = [
    ('diceExpression', diceparser.diceExpression)
])

class AttackOption(object):
    """A group of AttackForms which all may be used simultaneously"""
    def __init__(self):
        self.attackForms = []

    def __repr__(self):
        return '<AttackOption with forms %s>' % (
                [f for f in self.attackForms])

class AttackForm(object):
    """A series of attacks with the same weapon"""
    def __init__(self):
        self.extraDamage = ''
        self.crit = '20'
        self.count = 1
        self.touch = ''
        self.rangeInformation = ''

    def __repr__(self):
        return '<AttackForm %s|%s|%s|%s|%s|%s|%s|%s|%s>' % (self.count, 
                self.weapon, 
                ['%+d'%(b,) for b in self.bonus], 
                self.damage, 
                self.crit, self.extraDamage, self.type,
                self.touch,
                self.rangeInformation)

class Processor(disp.DispatchProcessor):
    def attackStat(self, (t,s1,s2,sub), buffer):
        self.attackOptions = []
        disp.dispatchList(self, sub, buffer)
        return self.attackOptions

    def empty(self, (t,s1,s2,sub), buffer):
        pass

    def count(self, (t,s1,s2,sub), buffer):
        self.attackForm.count = int(buffer[s1:s2])

    def bonusSequence(self, (t,s1,s2,sub), buffer):
        s = disp.getString((t,s1,s2,sub), buffer)
        bonuses = []
        for bonus in s.split('/'):
            bonuses.append(int(bonus))
        self.attackForm.bonus = bonuses

    def weapon(self, (t,s1,s2,sub), buffer):
        self.attackForm.weapon = disp.getString((t,s1,s2,sub), buffer).strip()

    def damageSet(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def parenDamage(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def damagePhrase(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def rangeSlot(self, (t,s1,s2,sub), buffer):
        self.attackForm.rangeInformation = disp.getString((t,s1+1,s2-1,sub), buffer)

    def subAttackForm1(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def subAttackForm2(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def damage(self, (t,s1,s2,sub), buffer):
        self.attackForm.damage = disp.getString((t,s1,s2,sub), buffer)

    def extraClause(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def extraDamage(self, (t,s1,s2,sub), buffer):
        ed = disp.getString((t,s1,s2,sub), buffer)
        self.attackForm.extraDamage = self.attackForm.extraDamage + ed

    def crit(self, (t,s1,s2,sub), buffer):
        self.attackForm.crit = disp.getString((t,s1,s2,sub), buffer)

    def attackTypeSlot(self, (t,s1,s2,sub), buffer):
        self.attackForm.type = disp.getString((t,s1,s2,sub), buffer)

    def cwb(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def anyAttackForm(self, (t,s1,s2,sub), buffer):
        form = AttackForm()
        self.option.attackForms.append(form)
        self.attackForm = form
        return disp.dispatchList(self, sub, buffer)

    def attackForm1(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def attackForm2(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def attackOption(self, (t,s1,s2,sub), buffer):
        self.option = AttackOption()
        self.attackOptions.append(self.option)
        return disp.dispatchList(self, sub, buffer)

    def attackTypeAndTouch(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def attackTouchSlot(self, (t,s1,s2,sub), buffer):
        return disp.dispatchList(self, sub, buffer)

    def staticNumber(self, (t,s1,s2,sub), buffer):
        self.expr.staticNumber = int(buffer[s1:s2])

if __name__ == '__main__':
    tests = query._allAttackStats()
    for id, test in tests:
        print id, test,
        suc, children, next = attackParser.parse(test, processor=Processor())
        print children
        assert next==len(test),  test[:next]
