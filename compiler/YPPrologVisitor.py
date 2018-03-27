#!/usr/bin/env python

from prologVisitor import prologVisitor

class Term:
    pass

class NumeralTerm(Term):
    def __init__(self,s):
        self.num = s
    def __str__(self):
        return self.num

class StringTerm(Term):
    def __init__(self,s):
        self.string = s
    def __str__(self):
        return self.string

class VariableTerm(Term):
    def __init__(self,s):
        self.varname = s
    def __str__(self):
        return self.varname

class Atom:
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    def generate(self,generator):
        return generator.generateAtom(self)

class Functor:
    def __init__(self,name,args):
        self.name = name
        self.args = args
    def __str__(self):
        return "%s(%s)" % (str(self.name),",".join([str(a) for a in self.args]))

class Clause:
    def __init__(self,head,body):
        self.head = head
        self.body = body
    def __str__(self):
        return "%s :- %s" % (str(self.head),str(self.body))


class YPPrologVisitor(prologVisitor):
    def __init__(self):
        prologVisitor.__init__(self)
        self.clauses = {}
    def visitProgram(self,ctx):
        self.visitChildren(ctx)
        return self.clauses
    def visitClause(self,ctx):
        lhs = self.visitPredicate(ctx.predicate())
        if ctx.predicatelist():
            rhs = self.visitPredicatelist(ctx.predicatelist())
        else:
            rhs = []
        # add to clauselist
        # clause(lhs/len(rhs))
        # print lhs
        c = Clause(lhs,rhs)
        # print c
        self.clauses.setdefault((lhs.name,len(lhs.args)),[]).append(c)
        # print self.clauses
        if rhs:
            return 'bla'
        else:
            return 'fact'
        pass

    def visitPredicate(self,ctx):
        atom = ctx.ATOM().getText()
        if ctx.termlist():
            termlist = self.visitTermlist(ctx.termlist())
            return Functor(atom,termlist)
        else:
            return Atom(atom)

    def visitTermlist(self,ctx):
        term = self.visitTerm(ctx.term())
        if ctx.termlist():
            termlist = self.visitTermlist(ctx.termlist())
        else:
            termlist = []
        return [ term ] + termlist
    def visitTerm(self,ctx):
        if ctx.NUMERAL() != None:
            return ctx.NUMERAL().getText()
        if ctx.STRING() != None:
            return ctx.STRING().getText()
        if ctx.VARIABLE() != None:
            variable = ctx.VARIABLE().getText()
            return variable
        if ctx.BINOP() != None:
            lterm = self.visitTerm(ctx.term(0))
            rterm = self.visitTerm(ctx.term(1))
            return "( ( %s ) %s ( %s ))" % (lterm, ctx.BINOP(),rterm)
        if ctx.predicate() != None:
            predicate = self.visitPredicate(ctx.predicate())
            return predicate
        if ctx.term() != None:
            term = self.visitTerm(ctx.term())
            return term

