#!/usr/bin/env python
#
# yldprolog - a rewrite of Yield Prolog
#
# This file is part of yldprolog.
#
# yldprolog is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License,
# version 3, as published by the Free Software Foundation.
#
# yldprolog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License, version 3, along with BANG.  If not, see
# <http://www.gnu.org/licenses/>
#
# Copyright 2018-2019 - Tim Hemel
# Licensed under the terms of the GNU Affero General Public License
# version 3
# SPDX-License-Identifier: AGPL-3.0-only


from .prologVisitor import prologVisitor
import functools

class PredicateList:
    def __init__(self,head,tail):
        self.head = head
        self.tail = tail

class PredicateAnd:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

class TruePredicate:
    def getVariables(self):
        return []
    def __str__(self):
        return "true"

class FailPredicate:
    def getVariables(self):
        return []
    def __str__(self):
        return "fail"

class CutPredicate:
    def getVariables(self):
        return []
    def __str__(self):
        return "!"

class Predicate:
    def __init__(self,functor):
        self.functor = functor
    def name(self):
        return self.functor.name.value
    def args(self):
        return self.functor.args
    def getVariables(self):
        return self.functor.getVariables()
    def __str__(self):
        return str(self.functor)

class ConjunctionPredicate:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    def getVariables(self):
        return self.lhs.getVariables() + self.rhs.getVariables()
    def __str__(self):
        return "( %s , %s )" % (str(self.lhs),str(self.rhs))

class DisjunctionPredicate:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    def getVariables(self):
        return self.lhs.getVariables() + self.rhs.getVariables()
    def __str__(self):
        return "( %s ; %s )" % (str(self.lhs),str(self.rhs))

class IfThenPredicate:
    def __init__(self,condition,action):
        self.condition = condition
        self.action = action
    def getVariables(self):
        return self.condition.getVariables() + self.action.getVariables()
    def __str__(self):
        return "( %s -> %s )" % (str(self.condition),str(self.action))

class NegationPredicate:
    def __init__(self,pred):
        self.pred = pred
    def __str__(self):
        return "( \\+ %s )" % str(self.pred)
    def getVariables(self):
        return self.pred.getVariables()

class Term:
    pass

class NumeralTerm(Term):
    def __init__(self,s):
        self.num = s
    def __str__(self):
        return self.num
    def getVariables(self):
        return []

class VariableTerm(Term):
    def __init__(self,s):
        self.varname = s
    def __str__(self):
        return self.varname
    def getVariables(self):
        return [ self.varname ]

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
        return functools.reduce(lambda x,y: x + y, [ v.getVariables() for v in self.items ], [])

class ListPairTerm(Term):
    def __init__(self,head,tail):
        self.head = head
        self.tail = tail
    def __str__(self):
        return ". ( %s , %s )" % (self.head, self.tail)
    def getVariables(self):
        return self.head.getVariables() + self.tail.getVariables()


class Atom:
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    def getVariables(self):
        return []

class Functor:
    def __init__(self,name,args):
        self.name = name
        self.args = args
    def __str__(self):
        return "%s(%s)" % (str(self.name),",".join([str(a) for a in self.args]))
    def getVariables(self):
        return functools.reduce(lambda x,y: x + y, [ v.getVariables() for v in self.args ], [])

class Clause:
    def __init__(self,head,body):
        self.head = head
        self.body = body
    def __str__(self):
        return "%s :- %s" % (str(self.head),str(self.body))


class YPPrologVisitor(prologVisitor):
    def __init__(self,options):
        self.options = options
        prologVisitor.__init__(self)
        self.clauses = {}
        self.anonymousVariableCounter = 0
        self.debug_indent = 0

    def __getattribute__(self, name):
        attr = prologVisitor.__getattribute__(self,name)
        if hasattr(attr, '__call__') and attr.__name__[:5] == 'visit' \
            and attr.__name__ not in ['visitTerminal', 'visitChildren', 'visit']:
            def decorated_func(*args, **kwargs):
                self._debug(f'{" "*2*self.debug_indent}{attr.__name__}, ctx = {args[0]!r} {"{"}')
                self.debug_indent += 1
                result = attr(*args, **kwargs)
                self.debug_indent -= 1
                self._debug(f'{" "*2*self.debug_indent}{"}"} -> {result} :: {result!r} # {attr.__name__}')
                return result
            return decorated_func
        else:
            return attr

    def _debug(self,*args):
        if self.options.debug:
            self.options.outfile.write('# ' + " ".join([str(a) for a in args]) + '\n')

    def visitProgram(self,ctx):
        for i,x in enumerate(ctx.clauseordirective()):
            r = self.visitClauseordirective(ctx.clauseordirective(i))
            if isinstance(r, Clause):
                self.clauses.setdefault((r.head.name(),len(r.head.args())),[]).append(c)
            else:
                # directive
                pass
        return self.clauses

    def visitClauseordirective(self,ctx):
        if ctx.clause() is not None:
            return self.visitClause(ctx.clause())
        else:
            return self.visitDirective(ctx.directive())


    def visitClause(self,ctx):
        # l =  self.visitChildren(ctx)
        # print('::: clause children', l)
        # return l
        # TODO make a clause for it ?
        lhs = self.visitSimplepredicate(ctx.simplepredicate())
        if ctx.predicateterm():
            rhs = self.visitPredicateterm(ctx.predicateterm())
        else:
            rhs = TruePredicate()
        c = Clause(lhs,rhs)
        # self.clauses.setdefault((lhs.name(),len(lhs.args())),[]).append(c)
        return ((lhs.name(), len(lhs.args())), c)

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
        if ctx.CUT() != None:
            return CutPredicate()
        if ctx.functor():
            functor = self.visitFunctor(ctx.functor())
            return Predicate(functor)
        if ctx.term() is not None:
            return self.visitTerm(ctx.term())

    def visitPredicateterm(self,ctx):
        if ctx.simplepredicate() != None:
            return self.visitSimplepredicate(ctx.simplepredicate())
        if ctx.op:
            if ctx.op.text == '\\+':
                predicateterm = self.visitPredicateterm(ctx.predicateterm(0))
                return NegationPredicate(predicateterm)
            if ctx.op.text == ',':
                lhs = self.visitPredicateterm(ctx.predicateterm(0))
                rhs = self.visitPredicateterm(ctx.predicateterm(1))
                return ConjunctionPredicate(lhs,rhs)
            if ctx.op.text == '->':
                lhs = self.visitPredicateterm(ctx.predicateterm(0))
                rhs = self.visitPredicateterm(ctx.predicateterm(1))
                return IfThenPredicate(lhs,rhs)
            if ctx.op.text == ';':
                lhs = self.visitPredicateterm(ctx.predicateterm(0))
                rhs = self.visitPredicateterm(ctx.predicateterm(1))
                return DisjunctionPredicate(lhs,rhs)
        # else: ( predicateterm )
        if ctx.predicateterm() != []:
            return self.visitPredicateterm(ctx.predicateterm(0))

    def visitFunctor(self,ctx):
        atom = self.visitAtom(ctx.atom())
        termlist = self.visitTermlist(ctx.termlist())
        return Functor(atom,termlist)

    def visitTermlist(self,ctx):
        terms = [ self.visitTerm(ctx.term(i)) for i in range(len(ctx.term())) ]
        return terms

    def visitTerm(self,ctx):

        if ctx.atom() != None:
            atom = self.visitAtom(ctx.atom())
            return atom
        if ctx.functor() != None:
            functor = self.visitFunctor(ctx.functor())
            return functor
        if ctx.BINOP() != None:
            lterm = self.visitTerm(ctx.term(0))
            rterm = self.visitTerm(ctx.term(1))
            return Functor(ctx.BINOP().getText(), [lterm, rterm])
            # return "( ( %s ) %s ( %s ))" % (lterm, ctx.BINOP(),rterm)
        #if ctx.predicate() != None:
        #    predicate = self.visitPredicate(ctx.predicate())
        #    return predicate
        if ctx.LBRACK() is not None:
            if ctx.VARIABLE() != None:
                # listpair
                term = self.visitTerm(ctx.term())
                if ctx.termlist() is not None:
                    terms = [term] + self.visitTermlist(ctx.termlist())
                else:
                    terms = [term]
                var = self.visitVARIABLE(ctx.VARIABLE())
                p = functools.reduce(lambda x,y: ListPairTerm(y,x), reversed(terms), var)
                return p
            else:
                # list with terms
                termlist = self.visitTermlist(ctx.termlist())
                return ListTerm(termlist)
        if ctx.VARIABLE() != None:
            return self.visitVARIABLE(ctx.VARIABLE())
        if ctx.term() != []:
            term = self.visitTerm(ctx.term())
            return term
        else:
            self._debug( "UNKNOWN TERM",ctx.getText() )

    def visitAtom(self,ctx):
        if ctx.NUMERAL() != None:
            return NumeralTerm(ctx.NUMERAL().getText())
        if ctx.STRING() != None:
            us = self.unquoteString(ctx.STRING().getText())
            return Atom(us)
        if ctx.ATOM() != None:
            return Atom(ctx.ATOM().getText())

    def visitVARIABLE(self,var):
        varname = var.getText()
        if varname == '_':
            variable = AnonymousVariableTerm(self.anonymousVariableCounter)
            self.anonymousVariableCounter += 1
        else:
            variable = VariableTerm(varname)
        return variable

    def unquoteString(self,s):
        i = 1 # skip first quote
        r = ""
        while i < len(s) -1:
            if s[i] == '\\':
                i += 1
            else:
                r += s[i]
                i += 1
        return r

