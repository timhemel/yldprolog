#!/usr/bin/env python

from prologVisitor import prologVisitor

class PredicateList:
    def __init__(self,head,tail):
        self.head = head
        self.tail = tail

class PredicateAnd:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

class TruePredicate:
    pass

class FailPredicate:
    pass

class Predicate:
    def __init__(self,functor):
        self.functor = functor
    def name(self):
        return self.functor.name.value
    def args(self):
        return self.functor.args
    def generate(self,generator,boundVars,depth):
        return generator.generatePredicate(self,boundVars,depth)

class ConjunctionPredicate:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    def generate(self,generator,boundVars,depth):
        return generator.generateConjunctionPredicate(self,boundVars,depth)

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

class AnonymousVariableTerm(VariableTerm):
    def __init__(self,num):
        self.num = num
        self.varname = 'x'+str(self.num+1)

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
        self.anonymousVariableCounter = 0
    def visitProgram(self,ctx):
        self.visitChildren(ctx)
        return self.clauses
    def visitClause(self,ctx):
        lhs = self.visitSimplepredicate(ctx.simplepredicate())
        if ctx.predicateterm():
            rhs = self.visitPredicateterm(ctx.predicateterm())
        else:
            rhs = TruePredicate()
        c = Clause(lhs,rhs)
        # print c
        print lhs.functor
        self.clauses.setdefault((lhs.name(),len(lhs.args())),[]).append(c)
        # print self.clauses

    def visitPredicatelist(self,ctx):
        predicateterm = self.visitPredicateterm(ctx.predicateterm())
        if ctx.predicatelist():
            predicatelist = self.visitPredicatelist(ctx.predicatelist())
        else:
            predicatelist = None
        return PredicateList(predicateterm,predicatelist)

    def visitSimplepredicate(self,ctx):
        if ctx.TRUE() != None:
            return TruePredicate()
        if ctx.FAIL() != None:
            return FailPredicate()
        #if ctx.atom():
        #    atom = self.visitAtom(ctx.atom())
        #    return Predicate(atom)
        if ctx.functor():
            functor = self.visitFunctor(ctx.functor())
            return Predicate(functor)

    def visitPredicateterm(self,ctx):
        if ctx.simplepredicate() != None:
            return self.visitSimplepredicate(ctx.simplepredicate())
        if ctx.op:
            if ctx.op.text == '\\+':
                predicateterm = self.visitPredicateterm(ctx.predicateterm())
                return NegationPredicate(predicateterm)
            if ctx.op.text == ',':
                lhs = self.visitPredicateterm(ctx.predicateterm(0))
                rhs = self.visitPredicateterm(ctx.predicateterm(1))
                return ConjunctionPredicate(lhs,rhs)
            if ctx.op.text == ';':
                lhs = self.visitPredicateterm(ctx.predicateterm(0))
                rhs = self.visitPredicateterm(ctx.predicateterm(1))
                return DisjunctionPredicate(lhs,rhs)

    def visitFunctor(self,ctx):
        atom = self.visitAtom(ctx.atom())
        termlist = self.visitTermlist(ctx.termlist())
        return Functor(atom,termlist)

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
        if ctx.atom() != None:
            atom = self.visitAtom(ctx.atom())
            return atom
        if ctx.BINOP() != None:
            lterm = self.visitTerm(ctx.term(0))
            rterm = self.visitTerm(ctx.term(1))
            return "( ( %s ) %s ( %s ))" % (lterm, ctx.BINOP(),rterm)
        #if ctx.predicate() != None:
        #    predicate = self.visitPredicate(ctx.predicate())
        #    return predicate
        if ctx.termlist() != None:
            if ctx.VARIABLE() != None:
                # list head,tail
                pass
            else:
                # list with just terms
                termlist = self.visitTermlist(ctx.termlist())
                return ListTerm(termlist)
        if ctx.VARIABLE() != None:
            varname = ctx.VARIABLE().getText()
            if varname == '_':
                variable = AnonymousVariableTerm(self.anonymousVariableCounter)
                self.anonymousVariableCounter += 1
            else:
                variable = VariableTerm(varname)
            return variable
        if ctx.term() != None:
            term = self.visitTerm(ctx.term())
            return term
    def visitAtom(self,ctx):
        if ctx.STRING() != None:
            return Atom(ctx.STRING().getText())
        if ctx.ATOM() != None:
            return Atom(ctx.ATOM().getText())

