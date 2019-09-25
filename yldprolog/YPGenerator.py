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

import functools
from .YPPrologVisitor import *

class YPCodeExpr:
    def __init__(self,expr):
        self.expr = expr
    def generate(self,generator):
        return generator.generateExpr(self)

class YPCodeVar:
    def __init__(self,name):
        self.name = name
    def generate(self,generator):
        return generator.generateVar(self)

class YPCodeValue:
    def __init__(self,val):
        self.val = val
    def generate(self,generator):
        return generator.generateValue(self)

class YPCodeList:
    def __init__(self,l):
        self.l = l
    def generate(self,generator):
        return generator.generateList(self)

class YPCodeAssign:
    def __init__(self,lhs,rhs):
        """lhs is an rhs assignment expression,
        rhs is a YPCodeExpr.
        """
        self.lhs = lhs
        self.rhs = rhs
    def generate(self,generator):
        return generator.generateAssign(self)

class YPCodeYieldFalse:
    def generate(self,generator):
        return generator.generateYieldFalse(self)

class YPCodeYieldTrue:
    def generate(self,generator):
        return generator.generateYieldTrue(self)

class YPCodeYieldBreak:
    def generate(self,generator):
        return generator.generateYieldBreak(self)

class YPCodeIf:
    def __init__(self,condition,trueCode,falseCode=[]):
        """condition is a YPCodeExpr
        trueCode is a list of YPCode statements
        falseCode is a list of YPCode statements
        """
        self.condition = condition
        self.trueCode = trueCode
        self.falseCode = falseCode
    def generate(self,generator):
        return generator.generateIf(self)

class YPCodeForeach:
    def __init__(self,loopExpression,loopCode):
        """loopExpression is a YPCodeExpr, loopCode is a list of YPCode statements."""
        self.loopExpression = loopExpression
        self.loopCode = loopCode
    def generate(self,generator):
        return generator.generateForeach(self)

class YPCodeCall:
    def __init__(self,func,args):
        """func is a string, args a list of YPCodeExpr"""
        self.func = func
        self.args = args
    def generate(self,generator):
        return generator.generateCall(self)

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
        return generator.generateFunction(self)

class YPCodeBreakableBlock:
    def __init__(self,label,body):
        """label is a string,
        body is a list of YPCode statements
        """
        self.label = label
        self.body = body
    def generate(self,generator):
        return generator.generateBreakableBlock(self)

class YPCodeBreakBlock:
    def __init__(self,label):
        """label is a string"""
        self.label = label
    def generate(self,generator):
        return generator.generateBreakBlock(self)

class YPCodeProgram:
    def __init__(self,functions):
        """functions is a list of YPCodeFunction objects."""
        self.functions = functions
    def generate(self,generator):
        return generator.generateProgram(self)


class YPPrologCompiler:
    def __init__(self,options):
        self.options = options
        self.boundVars = [ [] ]
        self.headArgsByPos = []
        self.cutIfCounter = 0
    def _debug(self,*args):
        if self.options.debug:
            self.options.outfile.write('# ' + " ".join([str(a) for a in args]) + '\n')
    def pushBoundVars(self,variables):
        self.boundVars.append(self.boundVars[-1] + variables)
    def popBoundVars(self):
        self.boundVars.pop()
    def filterFreeVariables(self,variables):
        return list(set([ v for v in variables if v not in self.boundVars[-1] ]))
    def compileProgram(self,program):
        funcs = []
        for func,clauses in program.items():
            body = functools.reduce(lambda x,y: x+y, [ self.compileFunctionBody(c) for c in clauses ], [] )
            funcs.append(self.compileFunction(func,body))
        return YPCodeProgram(funcs)
    def compileFunctionBody(self,clause):
        self.findClauseHeadVariableArguments(clause.head.functor.args)
        headVarArguments = self.compileClauseHeadVariableArguments(clause.head.functor.args)
        self.pushBoundVars( [ v for v in self.headArgsByPos if v != None ] )

        freeVarsHead = self.getFreeVariables(clause.head.functor)
        self.pushBoundVars(freeVarsHead)
        freeVarDeclarationCodeHead = self.compileFreeVariableDeclarations(freeVarsHead)

        freeVarsBody = self.getFreeVariables(clause.body)
        self.pushBoundVars(freeVarsBody)
        freeVarDeclarationCodeBody = self.compileFreeVariableDeclarations(freeVarsBody)


        bodyCode = self.compileBody(clause.body)
        argListUnificationCode = self.compileArgListUnification(clause.head.functor.args, bodyCode)

        self.popBoundVars()
        self.popBoundVars()
        self.popBoundVars()

        return headVarArguments + freeVarDeclarationCodeHead + freeVarDeclarationCodeBody + argListUnificationCode
    def compileFunction(self,func,body):
        funcargs = [ self.getArgumentVariable(i) for i in range(func[1]) ]
        return YPCodeFunction(func[0],funcargs,body)
    def compileVariableAssignments(self,variablesWithValues):
        code = []
        for var,val in variablesWithValues:
            code.append(self.compileVariableAssignment(var,val))
        return code
    def compileVariableAssignment(self,var,val):
        return YPCodeAssign(var,val)
    def compileVariableDeclarations(self,variables):
        code = []
        for v in variables:
            code.append(self.compileVariableAssignment(v,'variable()'))
        return code

    def compileBody(self,body):
        # :- A,B
        self._debug("DEBUG", body)
        if isinstance(body,ConjunctionPredicate):
            # if A is simple
            if isinstance(body.lhs,Predicate):
                if body.lhs.functor.name.value == '$CUTIF':
                    self._debug("$CUTIF, A")
                    label = body.lhs.functor.args[0].value
                    codeA = self.compileBody(body.rhs)
                    codeB = [ YPCodeBreakBlock(label) ]
                    return codeA + codeB
                else:
                    self._debug("A,B")
                    coderhs = self.compileBody(body.rhs)
                    return self.compilePredicate(body.lhs, coderhs)
            elif isinstance(body.lhs,CutPredicate):
                self._debug("(!,A) => A [yieldBreak]")
                codeA = self.compileBody(body.rhs)
                return codeA + [ YPCodeYieldBreak() ]
            elif isinstance(body.lhs,NegationPredicate):
                # for semidetnoneout => if (!A) { B }
                # else:
                self._debug("((\+ A),B) =>  (A -> fail ; true),B")
                return self.compileBody(
                    ConjunctionPredicate(
                        DisjunctionPredicate(
                            IfThenPredicate(body.lhs.pred,FailPredicate()),
                            TruePredicate()
                        ),
                        body.rhs
                    )
                )
            elif isinstance(body.lhs,ConjunctionPredicate): # A is complex
                self._debug("(A,B),C => A,(B,C)")
                return self.compileBody(
                        ConjunctionPredicate(body.lhs.lhs, ConjunctionPredicate(body.lhs.rhs,body.rhs))
                )
            elif isinstance(body.lhs,DisjunctionPredicate):
                # (A -> T ; B ), C  =>  A -> (T,C) ; B, C
                if isinstance(body.lhs.lhs,IfThenPredicate):
                    self._debug("(A -> T ; B ), C  =>  A -> (T,C) ; B, C")
                    return self.compileBody(
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
                    self._debug("( A ; B ) , C   =>  A,C ; B,C")
                    return self.compileBody(
                        DisjunctionPredicate(
                            ConjunctionPredicate(body.lhs.lhs,body.rhs),
                            ConjunctionPredicate(body.lhs.rhs,body.rhs)
                        )
                    )
            elif isinstance(body.lhs,IfThenPredicate):
                self._debug("(A -> T), B  =>  (A -> T ; fail), B")
                self._debug(body.lhs, body.rhs)
                # (A -> T), B  =>  (A -> T ; fail), B
                return self.compileBody(
                        ConjunctionPredicate(
                            DisjunctionPredicate(
                                IfThenPredicate(body.lhs.condition,body.lhs.action),
                                FailPredicate()
                            ),
                            body.rhs
                        ))
            # true , A  =>  A
            elif isinstance(body.lhs,TruePredicate):
                self._debug("true , A => A")
                return self.compileBody(body.rhs)
            elif isinstance(body.lhs,FailPredicate):
                self._debug("fail , _ ")
                return []
        elif isinstance(body,DisjunctionPredicate):
            # A -> T ; B     =>   breakableblock (  A , $CUTIF(CutIfLabel) , T ; B )
            if isinstance(body.lhs,IfThenPredicate):
                self._debug("A -> T ; B  => breakableBlock( ... )")
                cutIfLabel = self.getCutIfLabel()
                code = self.compileBody(
                    DisjunctionPredicate(
                        ConjunctionPredicate(
                            body.lhs.condition,
                            ConjunctionPredicate(
                                Predicate(Functor(Atom("$CUTIF"),[Atom(cutIfLabel)])),
                                body.lhs.action
                            )
                        ),
                        body.rhs
                    )
                )
                return [ YPCodeBreakableBlock(cutIfLabel,code) ]
            else:
                # else:  A ; B
                self._debug("A ; B")
                codelhs = self.compileBody(body.lhs)
                coderhs = self.compileBody(body.rhs)
                return codelhs + coderhs
        elif isinstance(body,IfThenPredicate):
            self._debug("[A  =>  A, true]  A -> T => (A -> T), true")
            return self.compileBody(ConjunctionPredicate(body, TruePredicate()))
        # :- functor(...)   A => A, true
        elif isinstance(body,Predicate):
            if body.functor.name.value == '$CUTIF':
                self._debug("$CUTIF", body.functor.args)
                return [ self.YPCodeBreakBlock(body.functor.args[0].value) ]
            else:
                self._debug("[A  =>  A, true]  A => A, true")
                return self.compileBody(ConjunctionPredicate(body, TruePredicate()))
        elif isinstance(body,NegationPredicate):
            self._debug("[A  =>  A, true]  (\+ A) => (\+ A), true")
            return self.compileBody(ConjunctionPredicate(body, TruePredicate()))
        # :- fail
        elif isinstance(body,FailPredicate):
            self._debug("[A  =>  A, true]  fail => fail, true")
            return self.compileBody(ConjunctionPredicate(body, TruePredicate()))
        # :- true
        elif isinstance(body,TruePredicate):
            # TODO: ? return, return True, yield False (depending on state)
            self._debug("true")
            return [ YPCodeYieldFalse() ]
        elif isinstance(body,CutPredicate):
            self._debug("!")
            # for det predicates => [return]
            # for semidet predicates => [ returntrue ]
            # else => [ yieldtrue, yieldbreak ]
            return [ YPCodeYieldTrue(), YPCodeYieldBreak() ]
        self._debug("UNK", body)
    def compilePredicate(self,pred,code):
        args = [ self.compileExpression(a) for a in pred.functor.args ]
        return [ YPCodeForeach(YPCodeCall('query',[YPCodeExpr(pred.functor.name.value),YPCodeList(args)]),code) ]
        

    def compileArgListUnification(self,functorargs,bodycode):
        code = bodycode
        for i in range(len(functorargs),0,-1):
            if self.headArgsByPos[i-1] == None:
                argvar = self.getArgumentVariable(i-1)
                code = self.compileUnification(argvar,functorargs[i-1],code)
        return code
    def compileUnification(self,var,val,code):
        return [ YPCodeForeach(YPCodeCall('unify',[YPCodeVar(var),self.compileExpression(val)]), code) ]
    def compileExpression(self,expr):
        if isinstance(expr,Atom):
            return YPCodeCall('atom',[YPCodeExpr(expr.value)])
        if isinstance(expr,VariableTerm):
            return YPCodeVar(expr.varname)
        if isinstance(expr,Functor):
            args = [ self.compileExpression(a) for a in expr.args ]
            return YPCodeCall('functor',[ YPCodeExpr(expr.name.value), YPCodeList(args) ])
        if isinstance(expr,NumeralTerm):
            return YPCodeValue(expr.num)
        if isinstance(expr,ListTerm):
            return self.compileList(expr)
        if isinstance(expr,ListPairTerm):
            return YPCodeCall('listpair',[ self.compileExpression(expr.head), self.compileExpression(expr.tail) ])
        self._debug("UNK EXPR", expr,repr(expr))
    def compileList(self,expr):
        self._debug("compileList:",expr)
        if expr.items == []:
            return YPCodeVar('ATOM_NIL')
        else:
            return YPCodeCall('makelist',[YPCodeList([ self.compileExpression(x) for x in expr.items ])])
            # return NIL
    def findClauseHeadVariableArguments(self,args):
        # gets all arguments that are variables from args
        self.headArgsByPos = []
        varcount = {}
        for i in range(len(args)):
            if isinstance(args[i],VariableTerm):
                self.headArgsByPos.append(args[i].varname)
                varcount.setdefault(args[i].varname,0)
                varcount[args[i].varname] += 1
            else:
                self.headArgsByPos.append(None)
        # that occur only once
        for i in range(len(args)):
            a = self.headArgsByPos[i]
            if a:
                if varcount[a] > 1:
                    self.headArgsByPos[i] = None
    def compileClauseHeadVariableArguments(self,args):
        code = []
        for i in range(len(args)):
            if self.headArgsByPos[i] != None:
                code.append( YPCodeAssign(YPCodeVar(args[i]),YPCodeVar(self.getArgumentVariable(i))) )
        return code
    def compileFreeVariableDeclarations(self,variables):
        code = [ self.compileVariableDeclaration(v) for v in variables ]
        return code
    def compileVariableDeclaration(self,var):
        return YPCodeAssign(YPCodeVar(var),YPCodeCall("variable",[]))
    def getArgumentVariable(self,i):
        return "arg"+str(i+1)
    def getLoopVariable(self):
        return "l"+str(self.looplevel+1)
    def getCutIfLabel(self):
        self.cutIfCounter += 1
        return "cutIf"+str(self.cutIfCounter)
    def getFreeVariables(self,expr):
        variables = expr.getVariables()
        return self.filterFreeVariables(variables)

_output_header = """#
# This code is generated by the yldprolog compiler.
#

"""

class YPPythonCodeGenerator:
    def __init__(self):
        self.loopLevel = 0
        self.tabwidth = 2
        self.indentation = 0
    def generate(self,code):
        """code is a YPCode, output is a string"""
        return _output_header + code.generate(self)
    def generateCodeList(self,l):
        parts = [ c.generate(self) for c in l ]
        return self.lines(*parts)
        # return functools.reduce(lambda x,y: x+y, parts, [])
    def generateProgram(self,program):
        funcs = [ func.generate(self) + self.nl() for func in program.functions]
        return self.lines(*funcs)
    def generateFunction(self,func):
        # TODO: check if functionname is a reserved word
        funcargs = ",".join(func.args)
        s = self.l("def %s(%s):" % (func.name, funcargs))
        self.indent()
        # the "ugly code" for breakable blocks doesn't hurt, generate it anyway
        unsetBreakCode = self.l("doBreak = False")
        wrapCode = self.l("for _ in [1]:")
        self.indent()
        code = self.generateCodeList(func.body)
        self.dedent()
        # breakCode = self.generateBreakCode() # level <= 1, not needed
        falseYieldCode = self.generateCodeList( [ YPCodeIf(YPCodeExpr(False),[YPCodeYieldFalse()]) ])
        self.dedent()
        return self.lines(s, unsetBreakCode, wrapCode, code, falseYieldCode)
    def generateIf(self,ifstatement):
        conditionCode = ifstatement.condition.generate(self)
        trueCode = self.generateCodeList(ifstatement.trueCode)
        falseCode = self.generateCodeList(ifstatement.falseCode)
        lines = [ self.l("if %s:" % conditionCode) ]
        self.indent()
        lines.append(self.l(trueCode))
        self.dedent()
        if falseCode:
            lines.append(self.l("else:"))
            self.indent()
            lines.append(self.l(falseCode))
            self.dedent()
        return self.lines(*lines)
    def generateForeach(self,loop):
        loopVar = self._getLoopVar()
        expression = loop.loopExpression.generate(self)
        s = self.l("for %s in %s:" % (loopVar,expression))
        self.indent()
        self._enterLoop()
        if loop.loopCode == []:
            code = [ self.l("pass") ]
        else:
            code = self.generateCodeList(loop.loopCode)
        self._leaveLoop()
        self.dedent()
        # if doBreak
        breakCode = self.generateBreakCode()
        return self.lines(s, code, breakCode)
    def generateCall(self,call):
        # TODO: check if functionname is a reserved word
        args = ",".join([ a.generate(self) for a in call.args ])
        s = "%s(%s)" % (call.func,args)
        return s
    def generateYieldFalse(self,yf):
        return self.l("yield False")
    def generateYieldTrue(self,yt):
        return self.l("yield True")
    def generateYieldBreak(self,yb):
        return self.l("return")
    def generateAssign(self,assign):
        return self.l("%s = %s" % (assign.lhs.generate(self),assign.rhs.generate(self)))
    def generateBreakableBlock(self, bb):
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
        breakCode = self.generateBreakCode()
        lines.append( breakCode )
        return self.lines(*lines)
    def generateBreakBlock(self,bb):
        lines = [ self.l("%s = True" % bb.label) ]
        lines.append( self.l("doBreak = True") )
        lines.append( self.l("break") )
        return self.lines(*lines)
    def generateBreakCode(self):
        lines = [ self.l("if doBreak:") ]
        self.indent()
        lines.append(self.l("break"))
        self.dedent()
        return self.lines(*lines)
    def generateVar(self,var):
        return var.name
    def generateExpr(self,expr):
        return repr(expr.expr)
    def generateList(self,expr):
        return "[" + ",".join( [ v.generate(self) for v in expr.l ] ) + "]"
    def generateValue(self,expr):
        return expr.val
    def _getLoopVar(self):
        return 'l'+str(self.loopLevel+1)
    def _enterLoop(self):
        self.loopLevel += 1
    def _leaveLoop(self):
        self.loopLevel -= 1
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

