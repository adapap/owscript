from string import capwords
from AST import *
from OWScriptVisitor import OWScriptVisitor
class ASTBuilder(OWScriptVisitor):
    """Builds an AST from a parse tree generated by ANTLR."""
    def visitScript(self, ctx):
        script = Script()
        for child in ctx.children:
            x = self.visit(child)
            if type(x) in (Function, Call):
                script.functions.append(x)
            elif type(x) == Ruleset:
                script.rulesets.append(x)
        return script

    def visitRuleset(self, ctx):
        ruleset = Ruleset()
        for child in ctx.children:
            ruleset.rules.append(self.visit(child))
        return ruleset

    def visitRuledef(self, ctx):
        rule = Rule()
        rule.rulename = self.visit(ctx.rulename())
        for rulebody in ctx.rulebody():
            rule.rulebody.append(self.visit(rulebody))
        return rule

    def visitRulename(self, ctx):
        return ctx.STRING()

    def visitRulebodyBlock(self, ctx):
        if ctx.RULEBLOCK():
            ruleblock = Ruleblock(type_=ctx.RULEBLOCK().getText())
            ruleblock.block = self.visit(ctx.ruleblock())
            return ruleblock
        return self.visit(ctx.RCall())

    def visitBlock(self, ctx):
        block = Block()
        for line in ctx.line():
            x = self.visit(line)
            if x:
                block.lines.append(x)
        return block

    def visitAdd(self, ctx):
        if len(ctx.children) > 1:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return BinaryOp(left=left, op='+', right=right)
        return self.visitChildren(ctx)

    def visitSub(self, ctx):
        if len(ctx.children) > 1:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return BinaryOp(left=left, op='-', right=right)
        return self.visitChildren(ctx)

    def visitMul(self, ctx):
        if len(ctx.children) > 1:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return BinaryOp(left=left, op='*', right=right)
        return self.visitChildren(ctx)

    def visitDiv(self, ctx):
        if len(ctx.children) > 1:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return BinaryOp(left=left, op='/', right=right)
        return self.visitChildren(ctx)

    def visitPow(self, ctx):
        if len(ctx.children) > 1:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return BinaryOp(left=left, op='^', right=right)
        return self.visitChildren(ctx)

    def visitMod(self, ctx):
        if len(ctx.children) > 1:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return BinaryOp(left=left, op='%', right=right)
        return self.visitChildren(ctx)


    def visitPrimary(self, ctx):
        if len(ctx.children) == 3:
            return self.visit(ctx.children[1])
        return self.visit(ctx.children[0])

    def visitLogic_or(self, ctx):
        if len(ctx.children) == 3:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return Or(left=left, op='or', right=right)
        return self.visitChildren(ctx)

    def visitLogic_and(self, ctx):
        if len(ctx.children) == 3:
            left = self.visit(ctx.children[0])
            right = self.visit(ctx.children[2])
            return And(left=left, op='and', right=right)
        return self.visitChildren(ctx)

    def visitLogic_not(self, ctx):
        if len(ctx.children) == 2:
            return Not(op='not', right=self.visit(ctx.children[1]))
        return self.visit(ctx.compare())

    def visitFuncdef(self, ctx):
        funcname = ctx.NAME().getText()
        funcbody = self.visit(ctx.funcbody())
        return Function(name=funcname, body=funcbody)

    def visitFuncbody(self, ctx):
        return self.visit(ctx.ruleset() or ctx.ruledef() or ctx.rulebody() or ctx.block())

    def visitAssign(self, ctx):
        assign = Assign()
        assign.left = self.visit(ctx.children[0])
        assign.op = ctx.ASSIGN().getText()
        assign.right = self.visit(ctx.expr())
        return assign

    def visitCompare(self, ctx):
        if len(ctx.children) == 3:
            compare = Compare()
            compare.left = self.visit(ctx.children[0])
            compare.op = ctx.children[1].getText()
            compare.right = self.visit(ctx.children[2])
            return compare
        return self.visit(ctx.arith()[0])

    def visitIf_stmt(self, ctx):
        expr = ctx.expr()
        block = ctx.block()
        if_cond = self.visit(expr[0])
        if_block = Ruleblock(block=self.visit(block[0]))
        elif_conds = []
        elif_blocks = []
        else_block = None
        if len(expr) > 1:
            elif_conds = [self.visit(x) for x in expr[1:]]
            if len(block) > len(expr):
                elif_blocks = [Ruleblock(block=self.visit(x)) for x in block[1:-1]]
                else_block = Ruleblock(block=self.visit(block[-1]))
            else:
                elif_blocks = [Ruleblock(block=self.visit(x)) for x in block[1:]]
        elif len(block) > len(expr):
            else_block = Ruleblock(block=self.visit(block[-1]))
        return If(cond=if_cond, block=if_block, elif_conds=elif_conds, elif_blocks=elif_blocks, else_block=else_block)

    def visitValue(self, ctx):
        value = Value(value=capwords(ctx.VALUE().getText()))
        for child in ctx.children:
            x = self.visit(child)
            if x:
                if type(x) == Block and not x.lines:
                    continue
                value.args.append(x)
        return value

    def visitAction(self, ctx):
        action = Action(value=capwords(ctx.ACTION().getText()))
        for child in ctx.children:
            x = self.visit(child)
            if x:
                if type(x) == Block and not x.lines:
                    continue
                action.args.append(x)
        return action

    def visitAfter_line(self, ctx):
        if len(ctx.children) == 3:
            return self.visit(ctx.children[1])
        return self.visit(ctx.children[0])

    def visitArg_list(self, ctx):
        arg_list = Block()
        for child in ctx.children:
            x = self.visit(child)
            if x:
                arg_list.lines.append(x)
        return arg_list

    def visitArray(self, ctx):
        array = Array()
        if len(ctx.children) == 3:
            array.elements = self.visit(ctx.children[1]).lines
        return array

    def visitItem(self, ctx):
        array = self.visit(ctx.children[0])
        index = self.visit(ctx.children[2])
        return Item(array=array, index=index)

    def visitName(self, ctx):
        text = ctx.NAME().getText()
        if text.startswith('Wait'):
            action = Action(value='Wait')
            action.args.append(Time(value=text.lstrip('Wait ')))
            return action
        return Name(value=ctx.NAME().getText())

    def visitConst(self, ctx):
        return Name(value=ctx.getText())

    def visitNumeral(self, ctx):
        return Numeral(value=ctx.num_const.text)

    def visitTime(self, ctx):
        return Time(value=ctx.getText())

    def visitVector(self, ctx):
        vector = Value(value='Vector')
        for child in ctx.children:
            x = self.visit(child)
            if x:
                if type(x) == Block and not x.lines:
                    continue
                vector.args.append(x)
        return vector

    def visitGlobal_var(self, ctx):
        gvar = GlobalVar(name=ctx.varname.text)
        return gvar

    def visitPlayer_var(self, ctx):
        pvar = PlayerVar(name=ctx.varname.text)
        if len(ctx.children) == 3:
            pvar.player = self.visit(ctx.children[-1])
        return pvar

    def visitRCall(self, ctx):
        func = self.visit(ctx.children[0])
        args = self.visit(ctx.children[1])
        return Call(func=func.name, args=args)

    def visitPCall(self, ctx):
        func = self.visit(ctx.children[0])
        args = self.visit(ctx.children[1])
        return Call(func=func.name, args=args)

    def visitCall(self, ctx):
        if ctx.arg_list():
            return self.visit(ctx.arg_list())
        return None

    def run(self, parse_tree):
        return self.visit(parse_tree)