class IUnifiable(object):
    pass

class Atom(IUnifiable):
    def __init__(self,name):
        self._name = name
    def name(self):
        return self._name
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
    def unify(self,term):
        arg = getValue(term)
        if isinstance(arg, Functor):
            if self._name.name() == arg._name.name():
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
    def atom(self,name):
        self._atomStore.setdefault(name,Atom(name))
        return self._atomStore[name]
    def variable(self):
        return Variable()
    def functor(self,name,*args):
        return Functor(name,args)


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

