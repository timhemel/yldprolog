
from YPPrologVisitor import *

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

class YPCodeList:
    def __init__(self,l):
        self.l = l
    def generate(self,generator):
        return generator.generateList(self)

class YPCodeAssign:
    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs
    def generate(self,generator):
        return generator.generateAssign(self)

class YPCodeYieldFalse:
    def generate(self,generator):
        return generator.generateYieldFalse(self)

class YPCodeForeach:
    def __init__(self,loopExpression,loopCode):
        self.loopExpression = loopExpression
        self.loopCode = loopCode
    def generate(self,generator):
        return generator.generateForeach(self)

class YPCodeCall:
    def __init__(self,func,args):
        self.func = func
        self.args = args
    def generate(self,generator):
        return generator.generateCall(self)

class YPCodeFunction:
    def __init__(self,name,args,body):
        self.name = name
        self.args = args
        self.body = body
    def generate(self,generator):
        return generator.generateFunction(self)

class YPCodeProgram:
    def __init__(self,functions):
        self.functions = functions
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
            body = reduce(lambda x,y: x+y, [ self.compileFunctionBody(c) for c in clauses ], [] )
            funcs.append(self.compileFunction(func,body))
        return YPCodeProgram(funcs)
    def compileFunctionBody(self,clause):
        # code = []
        headVarArguments = self.compileClauseHeadVariableArguments(clause.head.functor.args)
        # code.append( self.compileVariableAssignments(declVars) )
        # self.pushBoundVars([v[0] for v in declVars ])
        # :- true. (or empty body)
        if isinstance(clause.body,TruePredicate):
            # declare free variables
            # allVars = self.getVariablesFromArgumentList(clause.head.args())
            # freeVars = self.getUnboundVariables(allVars)
            # code.append(self.compileVariableDeclarations(freeVars))
            # unify
            b = self.compileArgListUnification(clause.head.functor.args)
        else:
            b = self.compileBody(clause.body)
        # return b
        return headVarArguments + [ b ]
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
        if isinstance(body,ConjunctionPredicate):
            # if A is simple
            if isinstance(body.lhs,Predicate):
                coderhs = self.compileBody(body.rhs)
                return self.compilePredicate(body.lhs, coderhs)
            elif isinstance(body.lhs,ConjunctionPredicate): # A is complex
                return self.compileBody(
                        ConjunctionPredicate(body.lhs.lhs, ConjunctionPredicate(body.lhs.rhs,body.rhs))
                )
        # :- functor(...)
        if isinstance(body,Predicate):
            code = self.compilePredicate(body,YPCodeYieldFalse())
            return code
        print "UNK", body
    def compilePredicate(self,pred,code):
        args = [ self.compileExpression(a) for a in pred.functor.args ]
        return YPCodeForeach(YPCodeCall('query',[YPCodeExpr(pred.functor.name.value),YPCodeList(args)]),code)
        

    def compileArgListUnification(self,functorargs,argindex=0):
        code = YPCodeYieldFalse()
        for i in range(len(functorargs),0,-1):
            argvar = self.getArgumentVariable(i-1)
            code = self.compileUnification(argvar,functorargs[i-1],code)
        return code
    def compileUnification(self,var,val,code):
        return YPCodeForeach(YPCodeCall('unify',[YPCodeVar(var),self.compileExpression(val)]), code)
    def compileExpression(self,expr):
        if isinstance(expr,Atom):
            return YPCodeCall('atom',[YPCodeExpr(expr.value)])
        if isinstance(expr,VariableTerm):
            return YPCodeVar(expr.varname)
    def compileClauseHeadVariableArguments(self,args):
        # gets all arguments that are variables from args
        code = []
        for i in range(len(args)):
            if isinstance(args[i],VariableTerm):
                code.append( YPCodeAssign(YPCodeVar(args[i]),YPCodeVar(self.getArgumentVariable(i))) )
        return code
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
        funcs = [ func.generate(self) + self.nl() for func in program.functions]
        return self.lines(*funcs)
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
        self._enterLoop()
        code = loop.loopCode.generate(self)
        self._leaveLoop()
        self.dedent()
        return self.lines(s, code)
    def generateCall(self,call):
        args = ",".join([ a.generate(self) for a in call.args ])
        s = "%s(%s)" % (call.func,args)
        return s
    def generateYieldFalse(self,yf):
        return self.l("yield False")
    def generateAssign(self,assign):
        return self.l("%s = %s" % (assign.lhs.generate(self),assign.rhs.generate(self)))
    def generateVar(self,var):
        return var.name
    def generateExpr(self,expr):
        return repr(expr.expr)
    def generateList(self,expr):
        return "[" + ",".join( [ v.generate(self) for v in expr.l ] ) + "]"
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






