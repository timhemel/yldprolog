class IUnifiable(object):
    pass

class Atom(IUnifiable):
    def __init__(self,name):
        self._name = name
    def name(self):
        return self._name
    def __str__(self):
        return "atom(%s)" % self._name
    def unify(self,term):
        arg = getValue(term)
        if isinstance(arg,Atom):
            if self._name == arg._name:
                return YPSuccess()
            else:
                return YPFail()
        elif isinstance(arg,Variable):
            return arg.unify(self)
        else:
            return YPFail()


class Variable(IUnifiable):
    def __init__(self):
        self._isBound = False
    def getValue(self):
        if not self._isBound: return self
        if isinstance(self._value,Variable):
            return self._value.getValue()
        return self._value
    def __str__(self):
        if self._isBound:
            return "var(%s)" % self._value
        return "var()"
    def unify(self,arg):
        if not self._isBound:
            self._value = getValue(arg)
            if self._value == self:
                yield False
            else:
                self._isBound = True
                try:
                    yield False
                finally:
                    self._isBound = False
        else: # is bound
            for l1 in unify(self,arg):
                yield False


class Functor(IUnifiable):
    def __init__(self,name,args):
        self._name = name
        self._args = args
    def __str__(self):
        args = ",".join([str(a) for a in self._args])
        return "%s(%s)" % (self._name,args)
    def unify(self,term):
        arg = getValue(term)
        if isinstance(arg, Functor):
            if self._name == arg._name:
                return unifyArrays(self._args,arg._args)
            else:
                return YPFail()
        elif isinstance(arg,Variable):
            return arg.unify(self)
        else:
            return YPFail()

class Answer:
    def __init__(self,values):
        self.values = values
    def match(self,args):
        return unifyArrays(args,self.values)

class YPFail(object):
    def __iter__(self):
        return self
    def next(self):
        raise StopIteration
    def close(self):
        pass

class YPSuccess(object):
    def __init__(self):
        self._done = False
    def __iter__(self):
        return self
    def next(self):
        if not self._done:
            self._done = True
            return False
        else:
            raise StopIteration
    def close(self):
        pass

def getValue(v):
    if isinstance(v,Variable): # TODO: does getValue only occur on Variable?
        return v.getValue()
    return v

def unify(term1,term2):
    arg1 = getValue(term1)
    arg2 = getValue(term2)
    # print "Unify:\n\t", term1,"\n\t", term2
    if isinstance(arg1,IUnifiable):
        return arg1.unify(arg2)
    elif isinstance(arg2,IUnifiable):
        return arg2.unify(arg1)
    else:
        if arg1 == arg2:
            return YPSuccess()
        else:
            return YPFail()

def unifyArrays(array1,array2):
    if len(array1) != len(array2):
        return
    iterators = [None]*len(array1)
    numIterators = 0
    gotMatch = True
    for i in range(len(array1)):
        iterators[i] = iter(unify(array1[i],array2[i]))
        numIterators += 1
        try:
            iterators[i].next()
        except StopIteration:
            gotMatch = False
            break
    try:
        if gotMatch:
            yield False
    finally:
        for i in range(numIterators):
            iterators[i].close()



class YP(object):
    def __init__(self):
        self._atomStore = {}
        self._predicatesStore = {}
        self.evalContext = {
                '__builtins__': {},
                'variable': self.variable,
                'atom': self.atom,
                'functor': self.functor,
                'functor1': self.functor1,
                'functor2': self.functor2,
                'functor3': self.functor3,
                'unify': unify,
                'True': True,
                'False': False,
        }
        self.evalBlacklist = self.evalContext.keys()
    def atom(self,name,module=None):
        self._atomStore.setdefault(name,Atom(name))
        return self._atomStore[name]
    def variable(self):
        return Variable()
    def functor(self,name,args):
        return Functor(name,args)
    def functor1(self,name,arg):
        return Functor(name,[arg])
    def functor2(self,name,arg1,arg2):
        return Functor(name,[arg1,arg2])
    def functor3(self,name,arg1,arg2,arg3):
        return Functor(name,[arg1,arg2,arg3])
    def loadScript(self,fn):
        execfile(fn,self.evalContext)
        # TODO: raise YPEngineException if loading fails
        print "Loaded script"
        for k,v in self.evalContext.items():
            print "\t%s -> %s" % (k,v)

    def _findPredicates(self,name,arity):
        try:
            return self._predicatesStore[(name.name(),arity)]
        except KeyError:
            raise Exception('TODO: unknown predicate')

    def _updatePredicate(self,name,arity,clauses):
        self._predicatesStore[(name.name(),arity)] = clauses

    def assertFact(self,name,values):
        """assert values at the end of the set of facts for the predicate with the
        name "name" and the arity len(values).
        "name" must be an Atom.
        values cannot contain unbound variables.
        """
        try:
            clauses = self._findPredicates(name,len(values))
            # indexedanswers
        except Exception,e:
            clauses = []
        clauses.append(Answer(values))
        self._updatePredicate(name,len(values),clauses)
    def query(self,name,args):
        try:
            if name not in self.evalBlacklist:
                print self.evalContext.keys()
                function = self.evalContext[name]
                return function(*args)
        except KeyError,e:
            pass
        except TypeError,e: # args not matching
            pass

        try:
            clauses = self._findPredicates(name,len(values))
        except Exception,e:
            pass
        # check if name is a defined fact or a defined clause
        print self.evalContext
        print self._predicatesStore
        print self._atomStore
        return self.matchDynamic(self.atom(name),args)

    def matchDynamic(self,name,args):
        """
        Match all clauses of the dynamic predicate with the name and with arity the length
        of the arguments.
        "name" must be an atom
        Returns an iterator.
        """
        pass
        clauses = self._findPredicates(name,len(args))

        return self.matchAllClauses(clauses, args)

    def matchAllClauses(self,clauses,args):
        for clause in clauses:
            for cut in clause.match(args):
                yield False
                if cut:
                    return

