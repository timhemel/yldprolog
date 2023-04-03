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
# License, version 3, along with yldprolog.  If not, see
# <http://www.gnu.org/licenses/>
#
# Copyright 2018-2019 - Tim Hemel
# Licensed under the terms of the GNU Affero General Public License
# version 3
# SPDX-License-Identifier: AGPL-3.0-only


import functools
import re
from .prologVisitor import prologVisitor
from .errors import CompilerError

class PredicateList:
    def __init__(self,head,tail):
        self.head = head
        self.tail = tail

class PredicateAnd:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

class TruePredicate:
    @property
    def variables(self):
        return []
    def __str__(self):
        return "true"

class FailPredicate:
    @property
    def variables(self):
        return []
    def __str__(self):
        return "fail"

class CutPredicate:
    @property
    def variables(self):
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
    @property
    def variables(self):
        return self.functor.variables
    def __str__(self):
        return str(self.functor)

class ConjunctionPredicate:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    @property
    def variables(self):
        return self.lhs.variables + self.rhs.variables
    def __str__(self):
        return "( %s , %s )" % (str(self.lhs),str(self.rhs))

class DisjunctionPredicate:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    @property
    def variables(self):
        return self.lhs.variables + self.rhs.variables
    def __str__(self):
        return f'( {self.lhs} ; {self.rhs} )'

class IfThenPredicate:
    def __init__(self,condition,action):
        self.condition = condition
        self.action = action
    @property
    def variables(self):
        return self.condition.variables + self.action.variables
    def __str__(self):
        return f'( {self.condition} -> {self.action} )'

class NegationPredicate:
    def __init__(self,pred):
        self.pred = pred
    def __str__(self):
        return f'( \\+ {self.pred} )'
    @property
    def variables(self):
        return self.pred.variables

class Term:
    pass

class NumeralTerm(Term):
    def __init__(self,s):
        self.num = s
    def __str__(self):
        return self.num
    @property
    def variables(self):
        return []

class VariableTerm(Term):
    def __init__(self,s):
        self.varname = s
    def __str__(self):
        return self.varname
    @property
    def variables(self):
        return [ self.varname ]

class AnonymousVariableTerm(VariableTerm):
    def __init__(self,num):
        self.num = num
        self.varname = f'x{self.num+1}'

class ListTerm(Term):
    def __init__(self,l):
        self.items = l
    def __str__(self):
        return f'[{",".join([ str(x) for x in self.items ])}]'
    @property
    def variables(self):
        return functools.reduce(lambda x,y: x + y, [ v.variables for v in self.items ], [])

class ListPairTerm(Term):
    def __init__(self,head,tail):
        self.head = head
        self.tail = tail
    def __str__(self):
        return f'. ( {self.head} , {self.tail} )'
    @property
    def variables(self):
        return self.head.variables + self.tail.variables


class Atom:
    def __init__(self,value):
        self.value = value
    def __str__(self):
        if re.match(r'[A-Za-z_]+', self.value):
            return self.value
        return repr(self.value)
    @property
    def variables(self):
        return []

class Functor:
    def __init__(self,name,args):
        self.name = name
        self.args = args
    def __str__(self):
        return f'{self.name}({",".join([str(a) for a in self.args])})'
    @property
    def variables(self):
        return functools.reduce(lambda x,y: x + y, [ v.variables for v in self.args ], [])

class Clause:
    def __init__(self,head,body):
        self.head = head
        self.body = body
    def __str__(self):
        return f'{self.head} :- {self.body}'


class YPPrologVisitor(prologVisitor):
    def __init__(self,context):
        self.context = context
        prologVisitor.__init__(self)
        self.anonymousVariableCounter = 0
        self.debug_indent = 0
        if self.context.debug_filename:
            self._debug(f'Parsing {self.context.current_source_file}')

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
        if self.context.debug_parser:
            self.context.outf.write('# ' + " ".join([str(a) for a in args]) + '\n')

    def visitProgram(self,ctx):
        clauses = {}
        for i,x in enumerate(ctx.clauseordirective()):
            r = self.visitClauseordirective(ctx.clauseordirective(i))
            if isinstance(r, Clause):
                clauses.setdefault((r.head.name(),len(r.head.args())),[]).append(r)
            else:
                # TODO: handle directives
                pass
        return clauses

    def visitClauseordirective(self,ctx):
        if ctx.clause() is not None:
            return self.visitClause(ctx.clause())
        else:
            return self.visitDirective(ctx.directive())


    def visitClause(self,ctx):
        lhs = self.visitSimplepredicate(ctx.simplepredicate())
        if ctx.predicateexpression():
            rhs = self.visitPredicateexpression(ctx.predicateexpression())
        else:
            rhs = TruePredicate()
        c = Clause(lhs,rhs)
        return c

    def visitPredicatelist(self,ctx):
        predicateexpression = self.visitPredicateexpression(ctx.predicateexpression())
        if ctx.predicatelist():
            predicatelist = self.visitPredicatelist(ctx.predicatelist())
        else:
            predicatelist = None
        return PredicateList(predicateexpression,predicatelist)

    def visitSimplepredicate(self,ctx):
        if ctx.TRUE() is not None:
            return TruePredicate()
        if ctx.FAIL() is not None:
            return FailPredicate()
        if ctx.CUT() is not None:
            return CutPredicate()
        if ctx.termpredicate() is not None:
            return self.visitTermpredicate(ctx.termpredicate())

    def visitTermpredicate(self, ctx):
        t = self.visitTerm(ctx.term())
        if isinstance(t, Atom):
            t = Functor(t,[])
        if not isinstance(t, Functor):
            raise CompilerError(self.context.current_source_file, ctx.term(), f"'{ctx.term().getText()}' is not a functor")
        return Predicate(t)

    def visitPredicateexpression(self,ctx):
        if ctx.simplepredicate() is not None:
            p = self.visitSimplepredicate(ctx.simplepredicate())
            return p
        if ctx.op:
            if ctx.op.text == '\\+':
                predicateexpression = self.visitPredicateexpression(ctx.predicateexpression(0))
                return NegationPredicate(predicateexpression)
            if ctx.op.text == ',':
                lhs = self.visitPredicateexpression(ctx.predicateexpression(0))
                rhs = self.visitPredicateexpression(ctx.predicateexpression(1))
                return ConjunctionPredicate(lhs,rhs)
            if ctx.op.text == '->':
                lhs = self.visitPredicateexpression(ctx.predicateexpression(0))
                rhs = self.visitPredicateexpression(ctx.predicateexpression(1))
                return IfThenPredicate(lhs,rhs)
            if ctx.op.text == ';':
                lhs = self.visitPredicateexpression(ctx.predicateexpression(0))
                rhs = self.visitPredicateexpression(ctx.predicateexpression(1))
                return DisjunctionPredicate(lhs,rhs)
        # else: ( predicateexpression )
        if ctx.predicateexpression() != []:
            return self.visitPredicateexpression(ctx.predicateexpression(0))

    def visitFunctor(self,ctx):
        atom = self.visitAtom(ctx.atom())
        termlist = self.visitTermlist(ctx.termlist())
        return Functor(atom,termlist)

    def visitTermlist(self,ctx):
        terms = [ self.visitTerm(ctx.term(i)) for i in range(len(ctx.term())) ]
        return terms

    def visitTerm(self,ctx):
        if ctx.atom() is not None:
            atom = self.visitAtom(ctx.atom())
            return atom
        if ctx.ATOM() is not None and ctx.NUMERAL() is not None:
            # TODO: handle atom/nr
            pass
        if ctx.functor() is not None:
            functor = self.visitFunctor(ctx.functor())
            return functor
        if ctx.UNOP() is not None:
            # TODO: check if we need unary operators
            term = self.visitTerm(ctx.term(0))
            return Functor(Atom(ctx.UNOP().getText()), [term])
        if ctx.BINOP() is not None:
            lterm = self.visitTerm(ctx.term(0))
            rterm = self.visitTerm(ctx.term(1))
            return Functor(Atom(ctx.BINOP().getText()), [lterm, rterm])
        if ctx.LBRACK() is not None:
            if ctx.VARIABLE() is not None:
                # listpair
                term = self.visitTerm(ctx.term(0))
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
        if ctx.VARIABLE() is not None:
            return self.visitVARIABLE(ctx.VARIABLE())
        if ctx.term() != []:
            term = self.visitTerm(ctx.term(0))
            return term
        else:
            self._debug('UNKNOWN TERM',ctx.getText() )

    def visitAtom(self,ctx):
        if ctx.NUMERAL() is not None:
            return NumeralTerm(ctx.NUMERAL().getText())
        if ctx.STRING() is not None:
            us = self.unquoteString(ctx.STRING().getText())
            return Atom(us)
        if ctx.ATOM() is not None:
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

