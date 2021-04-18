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

import sys
import itertools
import functools

class YPException(Exception):
    pass

class IUnifiable(object):
    """Base interface for all term types that can be unified."""
    pass

class Atom(IUnifiable):
    """A Prolog atom. Atoms with the same name will be the same object, i.e. there will never
    be two different atoms with the same name."""
    def __init__(self, name):
        self._name = name
    def name(self):
        return self._name
    def to_python(self):
        if self._name == '[]':
            return []
        return self._name
    def __str__(self):
        return "atom(%s)" % self._name
    def unify(self, term):
        arg = get_value(term)
        if isinstance(arg, Atom):
            if self._name == arg._name:
                return YPSuccess()
            else:
                return YPFail()
        elif isinstance(arg, Variable):
            return arg.unify(self)
        else:
            return YPFail()


class Variable(IUnifiable):
    """A Prolog variable. Variables can be inspected while iterating through the results of
    a query."""
    def __init__(self):
        self._is_bound = False
    def get_value(self):
        """if the variable is bound, return the bound value, otherwise return the variable
        object itself. Will resolve the value recursively for variables that are bound to
        another variable."""
        if not self._is_bound:
            return self
        if isinstance(self._value, Variable):
            return self._value.get_value()
        return self._value
    def to_python(self):
        v = self.get_value()
        if isinstance(v, Variable):
            return None
        return to_python(v)
    def __str__(self):
        if self._is_bound:
            return "var(%s)" % self._value
        return "var()"
    def unify(self, arg):
        if not self._is_bound:
            self._value = get_value(arg)
            if self._value == self:
                yield False
            else:
                self._is_bound = True
                try:
                    yield False
                finally:
                    self._is_bound = False
        else: # is bound
            for l1 in unify(self, arg):
                yield False


class Functor(IUnifiable):
    """A Prolog functor."""
    def __init__(self, name, args):
        """name is the name of the functor.
        args is a list of Prolog terms and contains the functor arguments.
        """
        self._name = name
        self._args = args
    def to_python(self):
        if self._name == ".":
            # listpair
            args = [to_python(self._args[0])] + to_python(self._args[1])
            return args
        else:
            args = [to_python(v) for v in self._args]
            return (self._name, args)
    def __str__(self):
        args = ",".join([str(a) for a in self._args])
        return "%s(%s)" % (self._name, args)
    def unify(self, term):
        arg = get_value(term)
        if isinstance(arg, Functor):
            if self._name == arg._name:
                return unify_arrays(self._args, arg._args)
            else:
                return YPFail()
        elif isinstance(arg, Variable):
            return arg.unify(self)
        else:
            return YPFail()

class Answer:
    """Datastructure to represent predicates/facts."""
    def __init__(self, values):
        self.values = values
    def match(self, args):
        return unify_arrays(args, self.values)

class YPFail(object):
    """Iterator that always stops."""
    def __iter__(self):
        return self
    def __next__(self):
        raise StopIteration
    def close(self):
        pass

class YPSuccess(object):
    """Iterator that produces a result once and then stops."""
    def __init__(self):
        self._done = False
    def __iter__(self):
        return self
    def __next__(self):
        if not self._done:
            self._done = True
            return False
        else:
            raise StopIteration
    def close(self):
        pass

def chain_functions(func1, func2):
    funcs = [f for f in [func1, func2] if f is not None]
    def chain(*args):
        return itertools.chain(*[f(*args) for f in funcs])
    return chain

def get_value(v):
    """Return the value of a Prolog term. Constants and functors will return themselves,
    variables will be expanded if bound. Does not recursively expand variables."""
    if isinstance(v, Variable):
        return v.get_value()
    return v

def to_python(v):
    """Return v as a Python data structure."""
    if isinstance(v, IUnifiable):
        return v.to_python()
    return v

def unify(term1, term2):
    """Tries to unify term1 and term2. After unification, variables in the terms will be bound.
    """
    arg1 = get_value(term1)
    arg2 = get_value(term2)
    # print "Unify:\n\t", term1,"\n\t", term2
    if isinstance(arg1, IUnifiable):
        return arg1.unify(arg2)
    elif isinstance(arg2, IUnifiable):
        return arg2.unify(arg1)
    else:
        if arg1 == arg2:
            return YPSuccess()
        else:
            return YPFail()

def unify_arrays(array1, array2):
    """Unifies two lists of terms."""
    if len(array1) != len(array2):
        return
    iterators = [None]*len(array1)
    num_iterators = 0
    got_match = True
    for i in range(len(array1)):
        iterators[i] = iter(unify(array1[i], array2[i]))
        num_iterators += 1
        try:
            next(iterators[i])
        except StopIteration:
            got_match = False
            break
    try:
        if got_match:
            yield False
    finally:
        for i in range(num_iterators):
            iterators[i].close()


class YP(object):
    """The YieldProlog engine."""
    def __init__(self):
        self._atom_store = {}
        self._predicates_store = {}
        self.ATOM_NIL = self.atom("[]")
        self.ATOM_DOT = "."
        self._set_default_eval_context()
        self.eval_blacklist = list(self.eval_context.keys())

    def _set_default_eval_context(self):
        self.eval_context = {
            '__builtins__': {},
            'variable': self.variable,
            'atom': self.atom,
            'functor': self.functor,
            'functor1': self.functor1,
            'functor2': self.functor2,
            'functor3': self.functor3,
            'listpair': self.listpair,
            'makelist': self.makelist,
            'ATOM_NIL': self.ATOM_NIL,
            'unify': unify,
            'match_dynamic': self.match_dynamic,
            'query': self.query,
            'True': True,
            'False': False,
        }

    def clear(self):
        """clears all defined atoms, variables, facts and rules."""
        self._atom_store = {}
        self._predicates_store = {}
        self._set_default_eval_context()

    def atom(self, name, module=None):
        """Create an atom with name name in this engine. The parameter module is ignored and
        present to be compatible with the output from the modified YieldProlog compiler.
        """
        self._atom_store.setdefault(name, Atom(name))
        return self._atom_store[name]
    def variable(self):
        """Create a variable in this engine."""
        return Variable()
    def functor(self, name, args):
        """Create a functor in this engine with name name and the list of Prolog terms args
        as the functor arguments."""
        return Functor(name, args)
    def functor1(self, name, arg):
        """Compatibility function for creating a functor with one argument."""
        return Functor(name, [arg])
    def functor2(self, name, arg1, arg2):
        """Compatibility function for creating a functor with two arguments."""
        return Functor(name, [arg1, arg2])
    def functor3(self, name, arg1, arg2, arg3):
        """Compatibility function for creating a functor with three arguments."""
        return Functor(name, [arg1, arg2, arg3])
    def listpair(self, head, tail):
        """Creates a Prolog listpair representing [head|tail]. An empty list is
        represented by the ATOM_NIL object member.
        Example:
            yp = YP()
            prologlist = yp.listpair(yp.atom('a'),yp.listpair(yp.atom('b'),yp.ATOM_NIL))
        """
        return Functor(self.ATOM_DOT, [head, tail])
    def makelist(self, l):
        """Creates a Prolog list from a Python list. l is a list of Prolog terms."""
        r = functools.reduce(lambda x, y: self.listpair(y, x), reversed(l), self.ATOM_NIL)
        return r

    def load_script_from_string(self, s, fn='', overwrite=True):
        """Loads a compiled (to Python) Prolog program. Any functions defined in this program will be
        available to the engine and can be used in queries.
        s is a string of Python code.
        fn is an optional filename.
        If overwrite is True, it will overwrite existing function definitions. Otherwise,
        function definitions will be combined. Functions with the same name but a different
        number of arguments will be overwritten or combined. This could cause runtime errors.
        """
        new_context = self.eval_context.copy()
        code = compile(s, fn, 'exec')
        exec(code, new_context)
        for k, v in new_context.items():
            if self.eval_context.get(k) != v: # difference!
                # combine
                if overwrite:
                    self.eval_context[k] = v
                else:
                    self.eval_context[k] = chain_functions(self.eval_context.get(k), v)
        # TODO: raise YPEngineException if loading fails

    def load_script_from_file(self, fn, overwrite=True):
        """Same as load_script_from_string, but from file fn."""

        with open(fn, "r") as f:
            self.load_script_from_string(f.read(), fn=fn, overwrite=overwrite)
    
    def register_function(self, name, func):
        """Makes the function func available to the engine with name name. This can be used
        to call custom functions. These function will have to behave as Prolog functions, i.e.
        they will need to yield boolean values.
        """
        self.eval_context[name] = func

    def _find_predicates(self, name, arity):
        try:
            return self._predicates_store[(name, arity)]
        except KeyError:
            raise YPException('Unknown predicate: %s/%d' % (name, arity))

    def _update_predicate(self, name, arity, clauses):
        self._predicates_store[(name.name(), arity)] = clauses

    def assert_fact(self, name, values):
        """From the original YieldProlog:

        assert values at the end of the set of facts for the predicate with the
        name "name" and the arity len(values).
        "name" must be an Atom.
        values cannot contain unbound variables.
        """
        try:
            clauses = self._find_predicates(name.name(), len(values))
            # indexedanswers
        except YPException as e:
            clauses = []
        clauses.append(Answer(values))
        self._update_predicate(name, len(values), clauses)
    def query(self, name, args):
        """Creates a Prolog query for the symbol name, with arguments args. name is a string,
        args is a list of Prolog terms. The query will only be constructed, but not evaluated.
        Returns a Python generator of boolean values.

        Example:

        yp = YP()
        yp.assert_fact(yp.atom('cat'),[yp.atom('tom')])
        V1 = yp.variable()
        q = yp.query('cat',[V1])
        r = [ V1.get_value() for r in q ]
        assert r == [ yp.atom('tom') ]
        """
        try:
            if name not in self.eval_blacklist:
                function = self.eval_context[name]
                return function(*args)
        except KeyError as e:
            pass
        except TypeError as e: # args not matching
            pass

        return self.match_dynamic(self.atom(name), args)

    def evaluate_bounded(self, query, projection_function, recursion_limit=200):
        """Evaluates a query, but limits the recursion depth to recursion_limit. If a query
        causes a recursion that is too deep, the query will be aborted and the results collected
        so far will be returned.
        projection_function is a function taking the generator value (False or True) and maps it
        to anything else, for example the value of an instantiated Variable.

        yp = YP()
        yp.assert_fact(yp.atom('cat'),[yp.atom('tom')])
        V1 = yp.variable()
        q = yp.query('cat',[V1])
        r = yp.evaluate_bounded(q,(lambda x: V1.get_value()))
        assert r == [ yp.atom('tom') ]
        """
        old_recursionlimit = sys.getrecursionlimit()
        result = []
        try:
            sys.setrecursionlimit(recursion_limit)
            result = []
            for x in query:
                result.append(projection_function(x))
        except RuntimeError:
            pass
        except StopIteration:
            pass
        finally:
            sys.setrecursionlimit(old_recursionlimit)
        return result

    def match_dynamic(self, name, args):
        """From the original YieldProlog:

        Match all clauses of the dynamic predicate with the name and with arity the length
        of the arguments.
        "name" must be an atom
        Returns an iterator.
        """
        try:
            clauses = self._find_predicates(name.name(), len(args))
            return self._match_all_clauses(clauses, args)
        except YPException:
            return YPFail()

    def _match_all_clauses(self, clauses, args):
        for clause in clauses:
            for cut in clause.match(args):
                yield False
                if cut:
                    return
