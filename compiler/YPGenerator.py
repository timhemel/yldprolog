
from YPPrologVisitor import *



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
        code = []
        for func,clauses in program.items():
            body = [ self.compileFunctionBody(c) for c in clauses ]
            code.append(self.compileFunction(func,body))
        return code    
    def compileFunctionBody(self,clause):
        code = []
        declVars = self.getVariablesFromClauseHeadArguments(clause.head.args())
        code.append( self.compileVariableAssignments(declVars) )
        self.pushBoundVars([v[0] for v in declVars ])
        print clause.body
        # :- true. (or empty body)
        if isinstance(clause.body,TruePredicate):
            # declare free variables
            allVars = self.getVariablesFromArgumentList(clause.head.args())
            freeVars = self.getUnboundVariables(allVars)
            code.append(self.compileVariableDeclarations(freeVars))
            # unify
            code.append(self.compileUnification(clause.head.functor))
        else:
            # compile body
            # iterate
            pass
        return code
    def compileFunction(self,func,body):
        code = []
        print func
        print body
        pass
        return code
    def compileVariableAssignments(self,variablesWithValues):
        code = []
        for var,val in variablesWithValues:
            code.append(self.compileVariableAssignment(var,val))
        return code
    def compileVariableAssignment(self,var,val):
        return '%s = %s' % (var,val)
    def compileVariableDeclarations(self,variables):
        code = []
        for v in variables:
            code.append(self.compileVariableAssignment(v,'variable()'))
        return code
    def compileUnification(self,functor):
        for i in range(functor.args):
            a = functor.args[i]
            loopvar = self.getLoopVariable(i) # TODO: offset
            self.code.append(self.compileArgumentUnification(a,loopvar))
        pass
    def getArgumentVariable(self,i):
        return "arg"+str(i+1)
    def getLoopVariable(self,i):
        return "l"+str(i+1)
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
            print clause
            self._emitVariableAssignments(clause.head.args())
            boundVars = self.getVariablesFromList(clause.head.args())
            if isinstance(clause.body,TruePredicate):
                self._emitUnifyWithArgs(clause.head.args(),[],0)
            else:
                self._emitClauseBody(clause.body,boundVars,0)
    def _emitClauseBody(self,body,boundVars,depth):
        print body
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



