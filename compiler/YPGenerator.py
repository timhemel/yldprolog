
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
        return self.output()
    def getArgVar(self,i):
        return 'arg'+str(i+1)
    def getLoopVar(self,i):
        return 'l'+str(i+1)
    def _createVarListOfLength(self,n):
        l = [ self.getArgVar(i) for i in range(n) ]
        return ",".join(l)
    def _emitPredicateDefinition(self,head):
        varlist = self._createVarListOfLength(head[1])
        s = "def %s(%s):\n" % (head[0],varlist)
        self._emit(s)
    def _emitUnifyWithArgs(self,args,argpos):
        if args == []:
            self._emit("yield False\n")
        else:
            loopvar = self.getLoopVar(argpos)
            argvar = self.getArgVar(argpos) # 'x'+str(argpos)
            argval = args[0].generate(self)
            s = "for %s in unify(%s, %s):\n" % (loopvar,argvar,argval)
            self._emit(s)
            self.indent()
            self._emitUnifyWithArgs(args[1:],argpos+1)
            self.dedent()
    def _emitPredicateBody(self,rules):
        for clause in rules:
            self._emitUnifyWithArgs(clause.head.args,0)
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
    def generateList(self,listTerm):
        l = [ x.generate(self) for x in listTerm.items ]
        return "makelist([%s])" % ",".join(l)
    def generateFunctor(self,functor):
        args = [ x.generate(self) for x in functor.args ]
        return "functor(%s,[%s])" % (functor.name, ",".join(args))
    def generateNumber(self,number):
        return number.num

