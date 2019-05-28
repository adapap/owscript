class AST:
    pass

class Program(AST):
    def __init__(self, definitions=None):
        self.definitions = definitions or []

    def __repr__(self):
        return f'{self.definitions}'

class Function(AST):
    def __init__(self, name, body=None):
        self.name = name
        self.body = body

    def __repr__(self):
        return f'{self.name}: {self.body}'

class Ruleset(AST):
    def __init__(self, rules=None):
        self.rules = rules or []

    def __repr__(self):
        return ('_' * 50 + '\n').join(repr(x) for x in self.rules)

class Rule(AST):
    def __init__(self, rulename, event=None, conditions=None, actions=None):
        self.rulename = rulename
        self.event = event
        self.conditions = conditions
        self.actions = actions

    def __repr__(self):
        return '{}\n\t{}\n\t{}\n\t{}\n' \
            .format(self.rulename, self.event, self.conditions, self.actions)

class Ruleblock(AST):
    def __init__(self, block=None):
        self.block = block

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.block}'

class Event(Ruleblock):
    pass

class Conditions(Ruleblock):
    pass

class Actions(Ruleblock):
    pass

class Block(AST):
    def __init__(self, statements=None):
        self.statements = statements or []

    def __repr__(self):
        return f'{self.statements}'

class Value(AST):
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []

    def __repr__(self):
        if self.args:
            return f'{self.name}: {self.args}'
        return f'{self.name}'

class GlobalVar(Value):
    def __repr__(self):
        return f'gVar {self.name}'

class PlayerVar(Value):
    def __init__(self, name, player='Event Player'):
        self.name = name
        self.player = 'Event Player'

    def __repr__(self):
        return f'pVar@({self.player}) {self.name}'

class Action(Value):
    pass

class Type(AST):
    def __init__(self, value, args=None):
        self.value = value
        self.args = args or []

    def __repr__(self):
        if self.args:
            return f'{self.value} {self.args}'
        return f'{self.value}'

class Number(Type):
    pass

class NumberConst(Type):
    pass

class Name(Type):
    pass

class Comment(Type):
    pass

class Time(Type):
    pass

class Array(AST):
    def __init__(self, values=None):
        self.values = values or []

    def __repr__(self):
        return f'Array: {self.values}'

class BinaryOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'{self.left} {self.op} {self.right}'

class Assign(BinaryOp):
    pass

class Compare(BinaryOp):
    pass

class UnaryOp(AST):
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def __repr__(self):
        return f'{self.op}{self.right}'

class Negate(UnaryOp):
    pass

class Empty(AST):
    def __repr__(self):
        return f'Empty'