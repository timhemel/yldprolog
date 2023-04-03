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

import itertools
from .yp_prolog_visitor import *

class YPCodeExpr:
    def __init__(self,expr):
        self.expr = expr
    def generate(self,generator):
        return generator.generate_expr(self)

class YPCodeVar:
    def __init__(self,name):
        self.name = name
    def generate(self,generator):
        return generator.generate_var(self)

class YPCodeValue:
    def __init__(self,val):
        self.val = val
    def generate(self,generator):
        return generator.generate_value(self)

class YPCodeList:
    def __init__(self,l):
        self.l = l
    def generate(self,generator):
        return generator.generate_list(self)

class YPCodeAssign:
    def __init__(self,lhs,rhs):
        """lhs is an rhs assignment expression,
        rhs is a YPCodeExpr.
        """
        self.lhs = lhs
        self.rhs = rhs
    def generate(self,generator):
        return generator.generate_assign(self)

class YPCodeYieldFalse:
    def generate(self,generator):
        return generator.generate_yield_false(self)

class YPCodeYieldTrue:
    def generate(self,generator):
        return generator.generate_yield_true(self)

class YPCodeYieldBreak:
    def generate(self,generator):
        return generator.generate_yield_break(self)

class YPCodeIf:
    def __init__(self,condition,true_code,false_code=[]):
        """condition is a YPCodeExpr
        true_code is a list of YPCode statements
        false_code is a list of YPCode statements
        """
        self.condition = condition
        self.true_code = true_code
        self.false_code = false_code
    def generate(self,generator):
        return generator.generate_if(self)

class YPCodeForeach:
    def __init__(self,loop_expression,loop_code):
        """loop_expression is a YPCodeExpr, loop_code is a list of YPCode statements."""
        self.loop_expression = loop_expression
        self.loop_code = loop_code
    def generate(self,generator):
        return generator.generate_foreach(self)

class YPCodeCall:
    def __init__(self,func,args):
        """func is a string, args a list of YPCodeExpr"""
        self.func = func
        self.args = args
    def generate(self,generator):
        return generator.generate_call(self)

class YPCodeFunction:
    def __init__(self,name,args,body):
        """name is a string?
        args is a list of strings, with names of argument variables,
        body is a list of YPCode statements
        """
        self.name = name
        self.args = args
        self.body = body
    def generate(self,generator):
        return generator.generate_function(self)

class YPCodeBreakableBlock:
    def __init__(self,label,body):
        """label is a string,
        body is a list of YPCode statements
        """
        self.label = label
        self.body = body
    def generate(self,generator):
        return generator.generate_breakable_block(self)

class YPCodeBreakBlock:
    def __init__(self,label):
        """label is a string"""
        self.label = label
    def generate(self,generator):
        return generator.generate_break_block(self)

class YPCodeProgram:
    def __init__(self,functions):
        """functions is a list of YPCodeFunction objects."""
        self.functions = functions
    def generate(self,generator):
        return generator.generate_program(self)


class YPPrologCompiler:
    def __init__(self,context):
        self.context = context
        self.bound_vars = [ [] ]
        self.head_args_by_pos = []
        self.cut_if_counter = 0
    def _debug(self,*args):
        if self.context.debug_generator:
            self.context.outf.write('# ' + " ".join([str(a) for a in args]) + '\n')
    def push_bound_vars(self,variables):
        self.bound_vars.append(self.bound_vars[-1] + variables)
    def pop_bound_vars(self):
        self.bound_vars.pop()
    def filter_free_variables(self,variables):
        return list(set([ v for v in variables if v not in self.bound_vars[-1] ]))
    def compile_program(self,program):
        funcs = []
        for func,clauses in program.items():
            self._debug(f'Compiling clauses for {func}')
            body = itertools.chain.from_iterable( self.compile_function_body(c) for c in clauses )
            funcs.append(self.compile_function(func,body))
        return YPCodeProgram(funcs)
    def compile_function_body(self,clause):
        self._debug(f'-- Clause: {clause.head} :- {clause.body}')
        self.find_clause_head_variable_arguments(clause.head.functor.args)
        head_var_arguments = self.compile_clause_head_variable_arguments(clause.head.functor.args)
        self.push_bound_vars( [ v for v in self.head_args_by_pos if v != None ] )

        free_vars_head = self.get_free_variables(clause.head.functor)
        self.push_bound_vars(free_vars_head)
        free_var_declaration_code_head = self.compile_free_variable_declarations(free_vars_head)

        free_vars_body = self.get_free_variables(clause.body)
        self.push_bound_vars(free_vars_body)
        free_var_declaration_code_body = self.compile_free_variable_declarations(free_vars_body)


        body_code = self.compile_body(clause.body)
        arg_list_unification_code = self.compile_arg_list_unification(clause.head.functor.args, body_code)

        self.pop_bound_vars()
        self.pop_bound_vars()
        self.pop_bound_vars()

        return head_var_arguments + free_var_declaration_code_head + free_var_declaration_code_body + arg_list_unification_code

    def compile_function(self,func,body):
        funcargs = [ self.get_argument_variable(i) for i in range(func[1]) ]
        return YPCodeFunction(func[0],funcargs,body)

    def compile_variable_assignments(self,variables_with_values):
        code = []
        for var,val in variables_with_values:
            code.append(self.compile_variable_assignment(var,val))
        return code

    def compile_variable_assignment(self,var,val):
        return YPCodeAssign(var,val)

    def compile_variable_declarations(self,variables):
        code = []
        for v in variables:
            code.append(self.compile_variable_assignment(v,'variable()'))
        return code

    def compile_body(self,body):
        # :- A,B
        self._debug(f'---- Body: {body} :: {body!r}')
        if isinstance(body,ConjunctionPredicate):
            # if A is simple
            if isinstance(body.lhs,Predicate):
                if body.lhs.functor.name.value == '$CUTIF':
                    self._debug("------ case: $CUTIF, A")
                    label = body.lhs.functor.args[0].value
                    code_a = self.compile_body(body.rhs)
                    code_b = [ YPCodeBreakBlock(label) ]
                    return code_a + code_b
                else:
                    self._debug("------ case: A,B")
                    coderhs = self.compile_body(body.rhs)
                    return self.compile_predicate(body.lhs, coderhs)
            elif isinstance(body.lhs,CutPredicate):
                self._debug("------ case: (!,A) => A [yieldBreak]")
                code_a = self.compile_body(body.rhs)
                return code_a + [ YPCodeYieldBreak() ]
            elif isinstance(body.lhs,NegationPredicate):
                # for semidetnoneout => if (!A) { B }
                # else:
                self._debug("------ case: ((\\+ A),B) =>  (A -> fail ; true),B")
                return self.compile_body(
                    ConjunctionPredicate(
                        DisjunctionPredicate(
                            IfThenPredicate(body.lhs.pred,FailPredicate()),
                            TruePredicate()
                        ),
                        body.rhs
                    )
                )
            elif isinstance(body.lhs,ConjunctionPredicate): # A is complex
                self._debug("------ case: (A,B),C => A,(B,C)")
                return self.compile_body(
                        ConjunctionPredicate(body.lhs.lhs, ConjunctionPredicate(body.lhs.rhs,body.rhs))
                )
            elif isinstance(body.lhs,DisjunctionPredicate):
                # (A -> T ; B ), C  =>  A -> (T,C) ; B, C
                if isinstance(body.lhs.lhs,IfThenPredicate):
                    self._debug("------ case: (A -> T ; B ), C  =>  A -> (T,C) ; B, C")
                    return self.compile_body(
                        DisjunctionPredicate(
                            IfThenPredicate(
                                body.lhs.lhs.condition,
                                ConjunctionPredicate(body.lhs.lhs.action,body.rhs)
                            ),
                            ConjunctionPredicate(body.lhs.rhs,body.rhs)
                        )
                    )
                # ( A ; B ) , C   =>  A,C ; B,C
                else:
                    self._debug("------ case: ( A ; B ) , C   =>  A,C ; B,C")
                    return self.compile_body(
                        DisjunctionPredicate(
                            ConjunctionPredicate(body.lhs.lhs,body.rhs),
                            ConjunctionPredicate(body.lhs.rhs,body.rhs)
                        )
                    )
            elif isinstance(body.lhs,IfThenPredicate):
                self._debug("------ case: (A -> T), B  =>  (A -> T ; fail), B")
                self._debug(body.lhs, body.rhs)
                # (A -> T), B  =>  (A -> T ; fail), B
                return self.compile_body(
                        ConjunctionPredicate(
                            DisjunctionPredicate(
                                IfThenPredicate(body.lhs.condition,body.lhs.action),
                                FailPredicate()
                            ),
                            body.rhs
                        ))
            # true , A  =>  A
            elif isinstance(body.lhs,TruePredicate):
                self._debug("------ case: true , A => A")
                return self.compile_body(body.rhs)
            elif isinstance(body.lhs,FailPredicate):
                self._debug("------ case: fail , _ ")
                return []
        elif isinstance(body,DisjunctionPredicate):
            # A -> T ; B     =>   breakableblock (  A , $CUTIF(CutIfLabel) , T ; B )
            if isinstance(body.lhs,IfThenPredicate):
                self._debug("------ case: A -> T ; B  => breakableBlock( ... )")
                cut_if_label = self.get_cut_if_label()
                code = self.compile_body(
                    DisjunctionPredicate(
                        ConjunctionPredicate(
                            body.lhs.condition,
                            ConjunctionPredicate(
                                Predicate(Functor(Atom("$CUTIF"),[Atom(cut_if_label)])),
                                body.lhs.action
                            )
                        ),
                        body.rhs
                    )
                )
                return [ YPCodeBreakableBlock(cut_if_label,code) ]
            else:
                # else:  A ; B
                self._debug("------ case: A ; B")
                codelhs = self.compile_body(body.lhs)
                coderhs = self.compile_body(body.rhs)
                return codelhs + coderhs
        elif isinstance(body,IfThenPredicate):
            self._debug("------ case: [A  =>  A, true]  A -> T => (A -> T), true")
            return self.compile_body(ConjunctionPredicate(body, TruePredicate()))
        # :- functor(...)   A => A, true
        elif isinstance(body,Predicate):
            if body.functor.name.value == '$CUTIF':
                self._debug("------ case: $CUTIF", body.functor.args)
                return [ self.YPCodeBreakBlock(body.functor.args[0].value) ]
            else:
                self._debug("------ case: [A  =>  A, true]  A => A, true")
                return self.compile_body(ConjunctionPredicate(body, TruePredicate()))
        elif isinstance(body,NegationPredicate):
            self._debug("------ case: [A  =>  A, true]  (\\+ A) => (\\+ A), true")
            return self.compile_body(ConjunctionPredicate(body, TruePredicate()))
        # :- fail
        elif isinstance(body,FailPredicate):
            self._debug("------ case: [A  =>  A, true]  fail => fail, true")
            return self.compile_body(ConjunctionPredicate(body, TruePredicate()))
        # :- true
        elif isinstance(body,TruePredicate):
            # TODO: ? return, return True, yield False (depending on state)
            self._debug("------ case: true")
            return [ YPCodeYieldFalse() ]
        elif isinstance(body,CutPredicate):
            self._debug("------ case: !")
            # for det predicates => [return]
            # for semidet predicates => [ returntrue ]
            # else => [ yieldtrue, yieldbreak ]
            return [ YPCodeYieldTrue(), YPCodeYieldBreak() ]
        self._debug("------ case: unknown!!", body)

    def compile_predicate(self,pred,code):
        args = [ self.compile_expression(a) for a in pred.functor.args ]
        return [ YPCodeForeach(YPCodeCall('query',[YPCodeExpr(pred.functor.name.value),YPCodeList(args)]),code) ]
        

    def compile_arg_list_unification(self,functorargs,bodycode):
        code = bodycode
        for i in range(len(functorargs),0,-1):
            if self.head_args_by_pos[i-1] == None:
                argvar = self.get_argument_variable(i-1)
                code = self.compile_unification(argvar,functorargs[i-1],code)
        return code
    def compile_unification(self,var,val,code):
        return [ YPCodeForeach(YPCodeCall('unify',[YPCodeVar(var),self.compile_expression(val)]), code) ]
    def compile_expression(self,expr):
        if isinstance(expr,Atom):
            return YPCodeCall('atom',[YPCodeExpr(expr.value)])
        if isinstance(expr,VariableTerm):
            return YPCodeVar(expr.varname)
        if isinstance(expr,Functor):
            args = [ self.compile_expression(a) for a in expr.args ]
            return YPCodeCall('functor',[ YPCodeExpr(expr.name.value), YPCodeList(args) ])
        if isinstance(expr,NumeralTerm):
            return YPCodeValue(expr.num)
        if isinstance(expr,ListTerm):
            return self.compile_list(expr)
        if isinstance(expr,ListPairTerm):
            return YPCodeCall('listpair',[ self.compile_expression(expr.head), self.compile_expression(expr.tail) ])
        self._debug("UNK EXPR", expr,repr(expr))
    def compile_list(self,expr):
        self._debug("compile_list:",expr)
        if expr.items == []:
            return YPCodeVar('ATOM_NIL')
        else:
            return YPCodeCall('makelist',[YPCodeList([ self.compile_expression(x) for x in expr.items ])])
            # return NIL
    def find_clause_head_variable_arguments(self,args):
        # gets all arguments that are variables from args
        self.head_args_by_pos = []
        varcount = {}
        for i in range(len(args)):
            if isinstance(args[i],VariableTerm):
                self.head_args_by_pos.append(args[i].varname)
                varcount.setdefault(args[i].varname,0)
                varcount[args[i].varname] += 1
            else:
                self.head_args_by_pos.append(None)
        # that occur only once
        for i in range(len(args)):
            a = self.head_args_by_pos[i]
            if a:
                if varcount[a] > 1:
                    self.head_args_by_pos[i] = None
    def compile_clause_head_variable_arguments(self,args):
        code = []
        for i in range(len(args)):
            if self.head_args_by_pos[i] != None:
                code.append( YPCodeAssign(YPCodeVar(args[i]),YPCodeVar(self.get_argument_variable(i))) )
        return code
    def compile_free_variable_declarations(self,variables):
        code = [ self.compile_variable_declaration(v) for v in variables ]
        return code
    def compile_variable_declaration(self,var):
        return YPCodeAssign(YPCodeVar(var),YPCodeCall("variable",[]))
    def get_argument_variable(self,i):
        return "arg"+str(i+1)
    def get_loop_variable(self):
        return "l"+str(self.looplevel+1)
    def get_cut_if_label(self):
        self.cut_if_counter += 1
        return "cutIf"+str(self.cut_if_counter)
    def get_free_variables(self,expr):
        variables = expr.variables
        return self.filter_free_variables(variables)

_output_header = '''#
# This code is generated by the yldprolog compiler.
#
'''

class YPPythonCodeGenerator:
    def __init__(self, context):
        self.context = context
        self.loop_level = 0
        self.tabwidth = 2
        self.indentation = 0
    def generate(self,code):
        """code is a YPCode, output is a string"""
        if self.context.debug_filename:
            s = f'# from {self.context.current_source_file}\n#\n\n'
        else:
            s = '\n'
        return _output_header + s + code.generate(self)
    def generate_code_list(self,l):
        parts = [ c.generate(self) for c in l ]
        return self.lines(*parts)
    def generate_program(self,program):
        funcs = [ func.generate(self) + self.nl() for func in program.functions]
        return self.lines(*funcs)
    def generate_function(self,func):
        # TODO: check if functionname is a reserved word
        funcargs = ",".join(func.args)
        s = self.l(f'def {func.name}_{len(func.args)}({",".join(func.args)}):')
        self.indent()
        # the "ugly code" for breakable blocks doesn't hurt, generate it anyway
        unset_break_code = self.l("doBreak = False")
        wrap_code = self.l("for _ in [1]:")
        self.indent()
        code = self.generate_code_list(func.body)
        self.dedent()
        # break_code = self.generate_break_code() # level <= 1, not needed
        false_yield_code = self.generate_code_list( [ YPCodeIf(YPCodeExpr(False),[YPCodeYieldFalse()]) ])
        self.dedent()
        return self.lines(s, unset_break_code, wrap_code, code, false_yield_code)
    def generate_if(self,ifstatement):
        condition_code = ifstatement.condition.generate(self)
        true_code = self.generate_code_list(ifstatement.true_code)
        false_code = self.generate_code_list(ifstatement.false_code)
        lines = [ self.l("if %s:" % condition_code) ]
        self.indent()
        lines.append(self.l(true_code))
        self.dedent()
        if false_code:
            lines.append(self.l("else:"))
            self.indent()
            lines.append(self.l(false_code))
            self.dedent()
        return self.lines(*lines)
    def generate_foreach(self,loop):
        loop_var = self._get_loop_var()
        expression = loop.loop_expression.generate(self)
        s = self.l("for %s in %s:" % (loop_var,expression))
        self.indent()
        self._enter_loop()
        if loop.loop_code == []:
            code = [ self.l("pass") ]
        else:
            code = self.generate_code_list(loop.loop_code)
        self._leave_loop()
        self.dedent()
        # if doBreak
        break_code = self.generate_break_code()
        return self.lines(s, code, break_code)
    def generate_call(self,call):
        # TODO: check if functionname is a reserved word
        args = ",".join([ a.generate(self) for a in call.args ])
        s = "%s(%s)" % (call.func,args)
        return s
    def generate_yield_false(self,yf):
        return self.l("yield False")
    def generate_yield_true(self,yt):
        return self.l("yield True")
    def generate_yield_break(self,yb):
        return self.l("return")
    def generate_assign(self,assign):
        return self.l("%s = %s" % (assign.lhs.generate(self),assign.rhs.generate(self)))
    def generate_breakable_block(self, bb):
        # label = False
        lines = [ self.l("%s = False" % bb.label) ]
        ## if body != []
        # for _ in [1]:
        if bb.body != []:
            lines.append( self.l("for _ in [1]:") )
            self.indent()
        #      {{ body }}
            lines.extend( [ c.generate(self) for c in bb.body ] )
            self.dedent()
        ## endif
        #   if label:
        lines.append(self.l("if %s:" % bb.label))
        self.indent()
        #      doBreak = False
        lines.append(self.l("doBreak = False"))
        self.dedent()
        #   if doBreak:
        #     break
        break_code = self.generate_break_code()
        lines.append( break_code )
        return self.lines(*lines)
    def generate_break_block(self,bb):
        lines = [ self.l("%s = True" % bb.label) ]
        lines.append( self.l("doBreak = True") )
        lines.append( self.l("break") )
        return self.lines(*lines)
    def generate_break_code(self):
        lines = [ self.l("if doBreak:") ]
        self.indent()
        lines.append(self.l("break"))
        self.dedent()
        return self.lines(*lines)
    def generate_var(self,var):
        return var.name
    def generate_expr(self,expr):
        return repr(expr.expr)
    def generate_list(self,expr):
        return "[" + ",".join( [ v.generate(self) for v in expr.l ] ) + "]"
    def generate_value(self,expr):
        return expr.val
    def _get_loop_var(self):
        return 'l'+str(self.loop_level+1)
    def _enter_loop(self):
        self.loop_level += 1
    def _leave_loop(self):
        self.loop_level -= 1
    def indent(self):
        self.indentation += 1
    def dedent(self):
        self.indentation -= 1
    def l(self,s):
        return " "*self.tabwidth*self.indentation+s
    def lines(self,*args):
        return "\n".join(args)
    def nl(self):
        return "\n"

