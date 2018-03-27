
class YPGenerator:
    def __init__(self):
        self.reset()
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
            loopvar = 'l'+str(argpos)
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
        self.s += self._indent * 4 * ' ' + s
    def indent(self,n=1):
        self._indent += n
    def dedent(self,n=1):
        self._indent -= n
    def output(self):
        return self.s
    def generateAtom(self,atom):
        return "atom(%s)" % repr(atom.value)

