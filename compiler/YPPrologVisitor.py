#!/usr/bin/env python

from prologVisitor import prologVisitor

class PredicateList:
    def __init__(self,head,tail):
        self.head = head
        self.tail = tail

class Term:
    pass

class NumeralTerm(Term):
    def __init__(self,s):
        self.num = s
    def __str__(self):
        return self.num
    def getVariables(self):
        return []
    def generate(self,generator):
        return generator.generateNumber(self)

class VariableTerm(Term):
    def __init__(self,s):
        self.varname = s
    def __str__(self):
        return self.varname
    def getVariables(self):
        return [ self.varname ]
    def generate(self,generator):
        return generator.generateVariable(self)

class ListTerm(Term):
    def __init__(self,l):
        self.items = l
    def __str__(self):
        return "[%s]" % ",".join([ str(x) for x in self.items ])
    def getVariables(self):
        return reduce(lambda x,y: x + y, [ v.getVariables() for v in self.items ], [])
    def generate(self,generator):
        return generator.generateList(self)


class Atom:
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    def getVariables(self):
        return []
    def generate(self,generator):
        return generator.generateAtom(self)

class Functor:
    def __init__(self,name,args):
        self.name = name
        self.args = args
    def __str__(self):
        return "%s(%s)" % (str(self.name),",".join([str(a) for a in self.args]))
    def getVariables(self):
        return reduce(lambda x,y: x + y, [ v.getVariables() for v in self.args ], [])
    def generate(self,generator):
        return generator.generateFunctor(self)

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
            rhs = None
        # add to clauselist
        # clause(lhs/len(rhs))
        # print lhs
        c = Clause(lhs,rhs)
        # print c
        self.clauses.setdefault((lhs.name.value,len(lhs.args)),[]).append(c)
        # print self.clauses
        if rhs:
            return 'bla'
        else:
            return 'fact'
        pass

    def visitPredicatelist(self,ctx):
        predicateterm = self.visitPredicateterm(ctx.predicateterm())
        if ctx.predicatelist():
            predicatelist = self.visitPredicatelist(ctx.predicatelist())
        else:
            predicatelist = None
        return PredicateList(predicateterm,predicatelist)

    def visitPredicate(self,ctx):
        atom = Atom(ctx.ATOM().getText())
        if ctx.termlist():
            termlist = self.visitTermlist(ctx.termlist())
            return Functor(atom,termlist)
        else:
            return atom

    def visitTermlist(self,ctx):
        term = self.visitTerm(ctx.term())
        if ctx.termlist():
            termlist = self.visitTermlist(ctx.termlist())
        else:
            termlist = []
        return [ term ] + termlist
    def visitTerm(self,ctx):
        if ctx.NUMERAL() != None:
            return NumeralTerm(ctx.NUMERAL().getText())
        if ctx.STRING() != None:
            return Atom(ctx.STRING().getText())
        if ctx.BINOP() != None:
            lterm = self.visitTerm(ctx.term(0))
            rterm = self.visitTerm(ctx.term(1))
            return "( ( %s ) %s ( %s ))" % (lterm, ctx.BINOP(),rterm)
        if ctx.predicate() != None:
            predicate = self.visitPredicate(ctx.predicate())
            return predicate
        if ctx.termlist() != None:
            if ctx.VARIABLE() != None:
                # list head,tail
                pass
            else:
                # list with just terms
                termlist = self.visitTermlist(ctx.termlist())
                return ListTerm(termlist)
        if ctx.VARIABLE() != None:
            variable = VariableTerm(ctx.VARIABLE().getText())
            return variable
        if ctx.term() != None:
            term = self.visitTerm(ctx.term())
            return term

