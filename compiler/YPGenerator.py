
from YPPrologVisitor import *

class YPCodeExpr:
    def __init__(self,expr):
        self.expr = expr
    def __str__(self):
        return self.expr
    def generate(self,generator):
        return generator.generateExpr(self)

class YPCodeAssign:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return "%s = %s" % (self.lhs,self.rhs)

class YPCodeYieldFalse:
    def __str__(self):
        return "yield False"
    def generate(self,generator):
        return generator.generateYieldFalse(self)

class YPCodeForeach:
    def __init__(self,loopExpression,loopCode):
        self.loopExpression = loopExpression
        self.loopCode = loopCode
    def __str__(self):
        return "foreach %s { %s }" % (self.loopExpression,self.loopCode)
    def generate(self,generator):
        return generator.generateForeach(self)

class YPCodeCall:
    def __init__(self,func,args):
        self.func = func
        self.args = args
    def __str__(self):
        return "%s(%s)" % (self.func,self.args)
    def generate(self,generator):
        return generator.generateCall(self)

class YPCodeFunction:
    def __init__(self,name,args,body):
        self.name = name
        self.args = args
        self.body = body
    def __str__(self):
        return "def %s(%s) {\n\t%s\n}" % (self.name,self.args,[str(line) for line in self.body])
    def generate(self,generator):
        return generator.generateFunction(self)

class YPCodeProgram:
    def __init__(self,functions):
        self.functions = functions
    def __str__(self):
        return "\n".join([str(f) for f in self.functions])
    def generate(self,generator):
        return generator.generateProgram(self)


class YPPrologCompiler:
    def __init__(self):
        self.boundVars = [ [] ]
    def pushBoundVars(self,variables):
        self.boundVars.append(variables)
    def popBoundVars(self):
        self.boundVars.pop()
    def getUnboundVariables(self,variables):
        return list(set([ v for v in variables if v not in self.boundVars[-1] ]))
    def compileProgram(self,program):
        funcs = []
        for func,clauses in program.items():
            body = [ self.compileFunctionBody(c) for c in clauses ]
            funcs.append(self.compileFunction(func,body))
        return YPCodeProgram(funcs)
    def compileFunctionBody(self,clause):
        code = []
        declVars = self.getVariablesFromClauseHeadArguments(clause.head.args())
        code.append( self.compileVariableAssignments(declVars) )
        self.pushBoundVars([v[0] for v in declVars ])
        # :- true. (or empty body)
        if isinstance(clause.body,TruePredicate):
            # declare free variables
            # allVars = self.getVariablesFromArgumentList(clause.head.args())
            # freeVars = self.getUnboundVariables(allVars)
            # code.append(self.compileVariableDeclarations(freeVars))
            # unify
            return self.compileArgListUnification(clause.head.functor.args)
        else:
            # compile body
            # iterate
            pass
        return code
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
    def compileArgListUnification(self,functorargs,argindex=0):
        code = YPCodeYieldFalse()
        for i in range(len(functorargs),0,-1):
            argvar = self.getArgumentVariable(i-1)
            code = self.compileUnification(argvar,functorargs[i-1],code)
        return code
    def compileUnification(self,var,val,code):
        return YPCodeForeach(YPCodeCall('unify',[YPCodeExpr(var),self.compileExpression(val)]), code)
    def compileExpression(self,expr):
        if isinstance(expr,Atom):
            return YPCodeCall('atom',[YPCodeExpr(expr.value)])
    def getArgumentVariable(self,i):
        return "arg"+str(i+1)
    def getLoopVariable(self):
        return "l"+str(self.looplevel+1)
    def getVariablesFromClauseHeadArguments(self,args):
        # gets all arguments that are variables from args
        variables = []
        for i in range(len(args)):
            if isinstance(args[i],VariableTerm):
                variables.append( (args[i],self.getArgumentVariable(i)) )
        return variables
    def getVariablesFromArgumentList(self,args):
        # gets all variables that are used in an argument list
        return reduce(lambda x,y: x + y, [ v.getVariables() for v in args ], [])




class YPPythonCodeGenerator:
    def __init__(self):
        self.loopLevel = 0
        self.tabwidth = 2
        self.indentation = 0
    def generate(self,code):
        return code.generate(self)
    def generateProgram(self,program):
        funcs = [ func.generate(self) for func in program.functions]
        return "\n".join(funcs)
    def generateFunction(self,func):
        funcargs = ",".join(func.args)
        s = self.l("def %s(%s):" % (func.name, funcargs))
        self.indent()
        parts = [ p.generate(self) for p in func.body ]
        self.dedent()
        return self.lines(s,*parts)
    def generateForeach(self,loop):
        loopVar = self._getLoopVar()
        expression = loop.loopExpression.generate(self)
        s = self.l("for %s in %s:" % (loopVar,expression))
        self.indent()
        code = loop.loopCode.generate(self)
        self.dedent()
        return self.lines(s, code)
    def generateCall(self,call):
        args = ",".join([ a.generate(self) for a in call.args ])
        s = "%s(%s)" % (call.func,args)
        return s
    def generateYieldFalse(self,yf):
        return self.l("yield False")
    def generateExpr(self,expr):
        return repr(expr.expr)
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









class YPGenerator:
    def __init__(self):
        self.reset()
        self._tabwidth=2
    def reset(self):
        self.s = ""
        self._indent = 0

    def generate(self,clauses):
        self.reset()
        for pred,rules in clauses.items():
            self._emitPredicateDefinition(pred)
            self.indent()
            self._emitPredicateBody(rules)
            self.dedent()
            self._emit('\n')
        return self.output()
    def getArgVar(self,i):
        return 'arg'+str(i+1)
    def getLoopVar(self,i):
        return 'l'+str(i+1)
    def _createVarListOfLength(self,n):
        l = [ self.getArgVar(i) for i in range(n) ]
        return ",".join(l)
    def getVariables(self,v):
        return v.getVariables()
    def getVariablesFromList(self,l):
        return reduce(lambda x,y: x + y, [ self.getVariables(v) for v in l ], [])
    def getUnboundVars(self,allVars,boundVars):
        return list(set([ v for v in allVars if v not in boundVars ]))
    def _emitPredicateDefinition(self,head):
        varlist = self._createVarListOfLength(head[1])
        s = "def %s(%s):\n" % (head[0],varlist)
        self._emit(s)
    def _emitVariableAssignments(self,args):
        for i in range(len(args)):
            if isinstance(args[i],VariableTerm):
                self._emit('%s = %s\n' % (args[i],self.getArgVar(i)))
    def _emitUnifyWithArgs(self,args,boundVars,argpos):
        if args == []:
            self._emit("yield False\n")
        else:
            # unify loopvar with args[0]
            allVars = self.getVariables(args[0])
            unboundVars = self.getUnboundVars(allVars,boundVars)
            self._emitVariableDeclarations(unboundVars)
            loopvar = self.getLoopVar(argpos)
            argvar = self.getArgVar(argpos) # 'x'+str(argpos)
            argval = args[0].generate(self)
            s = "for %s in unify(%s, %s):\n" % (loopvar,argvar,argval)
            self._emit(s)
            self.indent()
            self._emitUnifyWithArgs(args[1:],boundVars+unboundVars,argpos+1)
            self.dedent()
    def _emitPredicateBody(self,rules):
        for clause in rules:
            self._emitVariableAssignments(clause.head.args())
            boundVars = self.getVariablesFromList(clause.head.args())
            if isinstance(clause.body,TruePredicate):
                self._emitUnifyWithArgs(clause.head.args(),[],0)
            else:
                self._emitClauseBody(clause.body,boundVars,0)
    def _emitClauseBody(self,body,boundVars,depth):
        body.generate(self,boundVars,depth)
        # self._emit(s)
    def _emitVariableDeclarations(self,variables):
        for v in variables:
            self._emitVariableDeclaration(v)
    def _emitVariableDeclaration(self,v):
        self._emit('%s = variable()\n' % v)
    def _emit(self,s):
        self.s += self._indent * self._tabwidth * ' ' + s
    def indent(self,n=1):
        self._indent += n
    def dedent(self,n=1):
        self._indent -= n
    def output(self):
        return self.s
    def generateAtom(self,atom):
        return "atom(%s)" % repr(atom.value)
    def generateVariable(self,var):
        return var.varname
    def generateList(self,listTerm):
        l = [ x.generate(self) for x in listTerm.items ]
        return "makelist([%s])" % ",".join(l)
    def generateFunctor(self,functor):
        args = [ x.generate(self) for x in functor.args ]
        return "functor(%s,[%s])" % (functor.name, ",".join(args))
    def generateNumber(self,number):
        return number.num
    def generatePredicate(self,pred,boundVars,depth):
        loopvar = self.getLoopVar(depth)
        functorName = pred.functor.name
        functorArgs = ",".join([ a.generate(self) for a in pred.functor.args ])
        allVars = self.getVariables(pred.functor)
        unboundVars = self.getUnboundVars(allVars,boundVars)
        self._emitVariableDeclarations(unboundVars)
        s = 'for %s in query(%s,[%s]):\n' % (loopvar, functorName, functorArgs)
        self._emit(s)
        self.indent()
        #if body.tail != None:
        #    self._emitClauseBody(body.tail,boundVars+unboundVars,depth+1)
        #else:
        #    self._emit("yield False\n")
        self._emit("yield False\n")
        self.dedent()
    def generateConjunctionPredicate(self,pred,boundVars,depth):
        pred.lhs.generate(self,boundVars,depth)
        self.indent()
        # TODO: bound vars
        pred.rhs.generate(self,boundVars,depth)
        self.dedent()



