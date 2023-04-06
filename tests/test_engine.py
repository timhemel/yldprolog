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


import pytest
import sys
import os
import pathlib
from yldprolog.engine import YP
from yldprolog.engine import Atom
from yldprolog.engine import Answer
from yldprolog.engine import unify
from yldprolog.engine import to_python
from yldprolog.compiler import compile_prolog_from_file, compile_prolog_from_string

_DATA_DIR = pathlib.Path(os.path.dirname(__file__)) / 'data'

class TestContext:
    debug_filename = ''
    debug_parser = False
    debug_generator = False

@pytest.fixture
def get_compiled_file(tmp_path):
    # compile all prolog files
    def compile_file(fn):
        path = pathlib.Path(fn)
        s = compile_prolog_from_file(_DATA_DIR / path, TestContext)
        outfn = tmp_path / path.parent / (path.stem + '.py')
        with open(outfn,'w') as f:
            f.write(s)
        return outfn
    return compile_file

def test_setup_yp():
    yp = YP()
    yp.assert_fact(yp.atom('cat'), [yp.atom('tom')])
    V1 = yp.variable()
    args = [V1]
    q = yp.query('cat', args)
    r = [[v.get_value() for v in args] for r in q]
    assert r == [[yp.atom('tom')]]


def test_clear():
    yp = YP()
    yp.assert_fact(yp.atom('cat'), [yp.atom('tom')])
    yp.clear()
    V1 = yp.variable()
    args = [V1]
    q = yp.query('cat', args)
    r = [[v.get_value() for v in args] for r in q]
    assert r == []



def test_evaluate_bounded_projection_function():
    yp = YP()
    yp.assert_fact(yp.atom('cat'), [yp.atom('tom')])
    V1 = yp.variable()
    q = yp.query('cat', [V1])
    r = yp.evaluate_bounded(q, (lambda x: V1.get_value()))
    assert r == [yp.atom('tom')]


def test_match_example_horizontal_vertical():
    yp = YP()
    X = yp.variable()
    Y = yp.variable()
    X1 = yp.variable()
    Y1 = yp.variable()
    # vertical(seg(point(X,Y),point(X,Y1))).
    yp.assert_fact(yp.atom('vertical'), [
        yp.functor('seg', [
            yp.functor('point', [X, Y]),
            yp.functor('point', [X, Y1])
        ])
    ])
    # horizontal(seg(point(X,Y),point(X1,Y))).
    yp.assert_fact(yp.atom('horizontal'), [
        yp.functor('seg', [
            yp.functor('point', [X, Y]),
            yp.functor('point', [X1, Y])
        ])
    ])

    # q0 = yp.match_dynamic(yp.atom('vertical'), [
    q0 = yp.query('vertical', [
        yp.functor('seg', [
            yp.functor('point', [1, 1]),
            yp.functor('point', [1, 2])
        ])
    ])

    # q1 = yp.match_dynamic(yp.atom('vertical'), [
    q1 = yp.query('vertical', [
        yp.functor('seg', [
            yp.functor('point', [1, 1]),
            yp.functor('point', [2, Y])
        ])
    ])

    # q2 = yp.match_dynamic(yp.atom('horizontal'), [
    q2 = yp.query('horizontal', [
        yp.functor('seg', [
            yp.functor('point', [1, 1]),
            yp.functor('point', [2, Y])
        ])
    ])

    r0 = list(q0)
    r1 = list(q1)
    r2 = [Y.get_value() for r in q2]

    assert r0 == [False]
    assert r1 == []
    assert r2 == [1]


def test_match_answer_different_arity():
    yp = YP()
    a = Answer([yp.atom('tom')])
    r = list(a.match([yp.variable(), yp.variable()]))
    assert r == []

def test_match_answer_matching():
    yp = YP()
    a = Answer([yp.atom('tom')])
    v = yp.variable()
    r = [v.get_value() for x in a.match([v])]
    assert r == [yp.atom('tom')]

def test_match_answer_not_matching():
    yp = YP()
    a = Answer([yp.atom('tom'), yp.atom('cat')])
    r = list(a.match([yp.atom('tom'), yp.atom('mouse')]))
    assert r == []

def test_unify_atoms_equal():
    yp = YP()
    a1 = yp.atom('tom')
    a2 = yp.atom('tom')
    r = list(unify(a1, a2))
    assert r == [False]

def test_unify_atoms_different():
    yp = YP()
    a1 = yp.atom('tom')
    a2 = yp.atom('jerry')
    r = list(unify(a1, a2))
    assert r == []

def test_unify_variable_unbound():
    yp = YP()
    a1 = yp.atom('tom')
    v1 = yp.variable()
    r = [v1.get_value() for x in unify(v1, a1)]
    # assert r ==[False]
    assert r == [yp.atom('tom')]

def test_unify_variable_integer():
    yp = YP()
    v1 = yp.variable()
    r = [v1.get_value() for x in unify(v1, 5)]
    assert r == [5]

def test_unify_variable_with_variable():
    yp = YP()
    v1 = yp.variable()
    v2 = yp.variable()
    r = [(v1.get_value(), v2.get_value()) for x in unify(v1, v2)]
    assert len(r) == 1
    assert r[0][0] == r[0][1]

def test_unify_variable_complex_atom():
    yp = YP()
    a1 = yp.functor("point", [1, 1])
    v1 = yp.variable()
    r = [v1.get_value() for x in unify(v1, a1)]
    assert to_python(r[0]) == to_python(a1)

def test_unify_complex_atoms():
    yp = YP()
    v1 = yp.variable()
    v2 = yp.variable()
    a1 = yp.functor("point", [v1, 2])
    a2 = yp.functor("point", [1, v2])
    r = [(v1.get_value(), v2.get_value()) for x in unify(a1, a2)]
    assert r == [(1, 2)]

def test_unify_complex_atoms_not_matching():
    yp = YP()
    v1 = yp.variable()
    a1 = yp.functor("point", [v1, 2])
    a2 = yp.functor("point", [1, 1])
    r = [v1.get_value() for x in unify(a1, a2)]
    assert r == []

def test_unify_complex_atoms_free_variable():
    yp = YP()
    v1 = yp.variable()
    v2 = yp.variable()
    a1 = yp.functor("point", [v1, 2])
    a2 = yp.functor("point", [v2, 2])
    r = [(v1.get_value(), v2.get_value()) for x in unify(a1, a2)]
    assert len(r) == 1
    assert r[0][0] == r[0][1]

# lists
def test_unify_lists():
    yp = YP()
    v1 = yp.variable()
    l1 = yp.listpair(yp.atom("a"), yp.listpair(yp.atom("b"), yp.ATOM_NIL))
    l2 = yp.listpair(yp.atom("a"), yp.listpair(v1, yp.ATOM_NIL))
    r = [v1.get_value() for x in unify(l1, l2)]
    assert r == [yp.atom("b")]

def test_unify_lists_with_makelist():
    yp = YP()
    v1 = yp.variable()
    l1 = yp.listpair(yp.atom("a"), yp.listpair(yp.atom("b"), yp.ATOM_NIL))
    l2 = yp.makelist([yp.atom("a"), v1])
    r = [v1.get_value() for x in unify(l1, l2)]
    assert r == [yp.atom("b")]

def test_get_value_recursively():
    yp = YP()
    v = yp.variable()
    f = yp.functor("point", [v, yp.atom('b')])
    a = yp.atom('a')
    r = [f.get_value() for x in unify(v, a)]
    assert to_python(r[0]) == ('point', ['a','b'])


# test loading a script
def test_load_monkey_and_banana_script(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('monkey.prolog'))
    # canget(state(atdoor,onfloor,atwindow,hasnot))
    q = yp.query('canget', [yp.functor('state',
            [yp.atom('atdoor'), yp.atom('onfloor'),
            yp.atom('atwindow'), yp.atom('hasnot')])])
    # this query has infinitely many solutions, just get the first one
    assert next(q) == False


# test concurrency when sourcing scripts
def test_load_scripts_concurrently(get_compiled_file):
    yp1 = YP()
    yp2 = YP()
    yp1.load_script_from_file(get_compiled_file('script1a.prolog'))
    yp2.load_script_from_file(get_compiled_file('script1b.prolog'))
    X1 = yp1.variable()
    q1 = yp1.query('fact', [X1])
    X2 = yp2.variable()
    q2 = yp2.query('fact', [X2])
    r1 = [X1.get_value() for r in q1]
    r2 = [X2.get_value() for r in q2]
    assert r1 != r2

# test concurrency when asserting facts
def test_assert_facts_concurrently():
    yp1 = YP()
    yp2 = YP()
    yp1.assert_fact(yp1.atom('fact'), [yp1.atom('red')])
    yp2.assert_fact(yp2.atom('fact'), [yp2.atom('blue')])
    X1 = yp1.variable()
    q1 = yp1.query('fact', [X1])
    X2 = yp2.variable()
    q2 = yp2.query('fact', [X2])
    r1 = [X1.get_value() for r in q1]
    r2 = [X2.get_value() for r in q2]
    assert r1 != r2

# test implicit clauses with user defined functions
def test_user_defined_function():
    yp = YP()
    side_effects = []
    def func(arg1):
        # check if arg1 instantiated
        if isinstance(arg1, Atom) and arg1.name() != "blue":
            side_effects.append('not blue')
        for l1 in unify(arg1, yp.atom("blue")):
            yield False
    yp.register_function('func', func)
    q = yp.query('func', [yp.atom('red')])
    r = list(q)
    assert side_effects == ['not blue']

def test_register_function_variable_arities():
    yp = YP()
    side_effects = []
    def func(arg1, *args):
        side_effects.extend(to_python(x) for x in args)
        for l1 in unify(arg1, yp.atom("blue")):
            yield False
    yp.register_function('func', func, arity=-1)
    q = yp.query('func', [yp.atom('blue'), yp.atom('yellow'), yp.atom('green')])
    r = list(q)
    assert side_effects == ['yellow', 'green']

def test_facts_and_function():
    s = compile_prolog_from_string('''
    person(mike).
    person(joe).
    person(pete).
    person(zack).
    ''', TestContext)

    yp = YP()
    yp.assert_fact(yp.atom('person'), [yp.atom('tom')])
    yp.assert_fact(yp.atom('person'), [yp.atom('jerry')])
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('person', [v])
    r = [ to_python(v) for x in q ]
    assert r == [ 'tom', 'jerry', 'mike', 'joe', 'pete', 'zack' ]


def test_run_infinite_script(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('monkey.prolog'))
    # canget(state(atdoor,onfloor,atwindow,hasnot))
    q = yp.query('canget', [yp.functor('state', [yp.atom('atdoor'),
        yp.atom('onfloor'), yp.atom('atwindow'), yp.atom('hasnot')])])
    # this query has infinitely many solutions, just get the first one
    recursion_limit = sys.getrecursionlimit()
    r = yp.evaluate_bounded(q, lambda x: x)
    assert sys.getrecursionlimit() == recursion_limit
    assert len(r) >= 1

def test_run_lists_script(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('lists.prolog'))
    l = yp.makelist([yp.atom(x) for x in ['Johnny', 'Dee Dee', 'Joey',
        'Tommy', 'Marky', 'Richie', 'Elvis', 'C. J.']])
    q = yp.query('member', [yp.atom('Richie'), l])
    r = list(q)
    assert r == [False]
    v1 = yp.variable()
    v2 = yp.variable()
    v3 = yp.variable()
    q = yp.query('testlist', [yp.makelist([v1, v2, v3])])
    r = [[v1.get_value(), v2.get_value(), v3.get_value()] for x in q]
    assert r == [[yp.atom('red'), yp.atom('green'), yp.atom('blue')]]

def test_sploit_eval(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('eval.prolog'))
    q = yp.query('sploit', ['1+1'])
    r = list(q)
    assert r == []

def test_load_scripts_add_multiple_definitions(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('defs1.prolog'), overwrite=False)
    yp.load_script_from_file(get_compiled_file('defs2.prolog'), overwrite=False)
    v1 = yp.variable()
    v2 = yp.variable()
    v3 = yp.variable()
    q = yp.query('testlist', [yp.makelist([v1, v2, v3])])
    r = [(v1.get_value(), v2.get_value(), v3.get_value()) for x in q]
    assert set(r) == set([
        (yp.atom('red'), yp.atom('green'), yp.atom('blue')),
        (yp.atom('cyan'), yp.atom('magenta'), yp.atom('yellow'))
    ])

def test_load_scripts_overwrite_multiple_definitions(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('defs1.prolog'), overwrite=True)
    yp.load_script_from_file(get_compiled_file('defs2.prolog'), overwrite=True)
    v1 = yp.variable()
    v2 = yp.variable()
    v3 = yp.variable()
    q = yp.query('testlist', [yp.makelist([v1, v2, v3])])
    r = [(v1.get_value(), v2.get_value(), v3.get_value()) for x in q]
    assert set(r) == set([
        (yp.atom('cyan'), yp.atom('magenta'), yp.atom('yellow'))
    ])

def test_query_without_predicates():
    yp = YP()
    v1 = yp.variable()
    q = yp.query('nonexistentpred', [v1])
    r = list(q)
    assert r == []

def test_query_operator_equals():
    yp = YP()
    v1 = yp.variable()
    q = yp.query('=', [v1, v1])
    r = list(q)
    assert len(r) == 1

def test_query_operator_neq():
    yp = YP()
    v1 = yp.variable()
    q = yp.query('/=', [v1, v1])
    r = list(q)
    assert len(r) == 0

def test_query_operator_neq_atom_var():
    yp = YP()
    v1 = yp.variable()
    a1 = yp.atom(1)
    q = yp.query('/=', [a1, v1])
    r = list(q)
    assert len(r) == 0

def test_query_operator_neq_atom_atom():
    yp = YP()
    # v1 = yp.variable()
    a1 = yp.atom(1)
    a2 = yp.atom(2)
    q = yp.query('\\=', [a1, a2])
    r = list(q)
    assert len(r) == 1

def test_builtin_predicate_findall():
    s = compile_prolog_from_string('''
    age(peter, 7).
    age(ann, 5).
    age(pat, 8).
    age(tom, 5).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v_child = yp.variable()
    v_age = yp.variable()
    v_list = yp.variable()

    q = yp.query('age', [v_child, v_age])
    result1 = [ to_python(v_child) for x in q ]
    assert result1 == ['peter', 'ann', 'pat', 'tom' ]

    q = yp.query('age', [v_child, 5])
    result2 = [ to_python(v_child) for x in q ]
    assert result2 == [ 'ann', 'tom' ]

    goal1 = yp.functor("age", [v_child, v_age])
    q = yp.query('findall', [v_child, goal1, v_list])
    r = [ to_python(v_list) for x in q ]
    assert len(r) == 1
    assert r[0] == result1

    goal2 = yp.functor("age", [v_child, 5])
    q = yp.query('findall', [v_child, goal2, v_list])
    r = [ to_python(v_list) for x in q ]
    assert len(r) == 1
    assert r[0] == result2

def test_builtin_predicate_call():
    s = compile_prolog_from_string('''
    age(peter, 7).
    age(ann, 5).
    age(pat, 8).
    age(tom, 5).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v_child = yp.variable()
    v_age = yp.variable()
    f_age = yp.functor('age', [v_child, 5])

    q = yp.query('age', [v_child, 5])
    result1 = [ to_python(v_child) for x in q ]
    assert result1 == [ 'ann', 'tom' ]

    q = yp.call(f_age)
    result2 = [ to_python(v_child) for x in q ]
    assert result2 == result1

    q = yp.query('call', [f_age])
    result3 = [ to_python(v_child) for x in q ]
    assert result3 == result1

    q = yp.query('call', [yp.functor('age',[v_child]), 5])
    result4 = [ to_python(v_child) for x in q ]
    assert result4 == result1

    q = yp.query('call', [yp.atom('age'), v_child, 5])
    result5 = [ to_python(v_child) for x in q ]
    assert result5 == result1

def test_builtin_predicate_once():
    s = compile_prolog_from_string('''
    age(peter, 7).
    age(ann, 5).
    age(pat, 8).
    age(tom, 5).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v_child = yp.variable()
    v_age = yp.variable()
    f_age = yp.functor('age', [v_child, v_age])

    q = yp.once(f_age)
    result1 = [ to_python(v_child) for x in q ]
    assert result1 == [ 'peter' ]

    q = yp.query('once', [f_age])
    result2 = [ to_python(v_child) for x in q ]
    assert result2 == result1

def test_builtin_predicate_assertaz():
    s = compile_prolog_from_string('''
    initp() :- assertz(p(b)), assertz(p(a)), asserta(p(c)).
    isp(X) :- initp() , p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('isp', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'c', 'b', 'a' ]

def test_builtin_predicate_asserta_multiple():
    s = compile_prolog_from_string('''
    initp() :- assertz(p(a)), assertz(p(a)), assertz(p(b)), asserta(p(c)).
    isp(X) :- initp() , p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('isp', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'c', 'a', 'a', 'b' ]

def test_builtin_predicate_assertz_instantiated_variable():
    s = compile_prolog_from_string('''
    name(tom).
    name(jerry).
    initp() :- name(Y), assertz(p(Y)).
    isp(X) :- p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    q = yp.query('initp', [ ])
    r = list(q)
    v = yp.variable()
    q = yp.query('isp', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'tom', 'jerry' ]

def test_builtin_predicate_assertz_free_variable():
    s = compile_prolog_from_string('''
    name(tom).
    name(jerry).
    initp() :- assertz(p(_)).
    isp(X) :- name(X), p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    q = yp.query('initp', [ ])
    r = list(q)
    v = yp.variable()
    q = yp.query('isp', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'tom', 'jerry' ]

def test_builtin_predicate_retract_single_atom():
    s = compile_prolog_from_string('''
    foo(X) :- assertz(p(b)), assertz(p(a)), asserta(p(c)), retract(p(a)), p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('foo', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'c', 'b' ]

def test_builtin_predicate_retract_duplicate_atom():
    s = compile_prolog_from_string('''
    foo(X) :- assertz(p(b)), assertz(p(a)), assertz(p(a)), asserta(p(c)), retract(p(a)), p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('foo', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'c', 'b', 'a', 'c', 'b' ]

def test_builtin_predicate_retract_var():
    s = compile_prolog_from_string('''
    foo(X) :- assertz(p(b)), assertz(p(a)), assertz(p(a)), asserta(p(c)), retract(p(_)), p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('foo', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'b', 'a', 'a', 'a', 'a', 'a' ]

def test_builtin_predicate_retractall_atom():
    s = compile_prolog_from_string('''
    foo(X) :- assertz(p(b)), assertz(p(a)), assertz(p(a)), asserta(p(c)), retractall(p(a)), p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('foo', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ 'c', 'b' ]

def test_builtin_predicate_retractall_var():
    s = compile_prolog_from_string('''
    foo(X) :- assertz(p(b)), assertz(p(a)), assertz(p(a)), asserta(p(c)), retractall(p(_)), p(X).
    ''', TestContext)
    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    v = yp.variable()
    q = yp.query('foo', [ v ])
    r = [ to_python(v) for x in q ]
    assert r == [ ]

def test_load_scripts_with_dependencies_in_order(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('subscript.prolog'), overwrite=False)
    yp.load_script_from_file(get_compiled_file('mainscript.prolog'), overwrite=False)
    v1 = yp.variable()
    q = yp.query('main', [v1])
    r = [v1.get_value() for x in q]
    assert r == [yp.atom('yes'), yp.atom('no'), yp.atom('maybe')]

def test_load_scripts_with_dependencies_out_of_order(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('mainscript.prolog'), overwrite=False)
    yp.load_script_from_file(get_compiled_file('subscript.prolog'), overwrite=False)
    v1 = yp.variable()
    q = yp.query('main', [v1])
    r = [v1.get_value() for x in q]
    assert r == [yp.atom('yes'), yp.atom('no'), yp.atom('maybe')]

def test_load_clauses_with_functors(get_compiled_file):
    yp = YP()
    yp.load_script_from_file(get_compiled_file('geometricobjects.prolog'), overwrite=False)
    Y = yp.variable()
    q = yp.query('horizontal', [
        yp.functor('seg', [
            yp.functor('point', [1, 1]),
            yp.functor('point', [2, Y])
        ])
    ])
    r = [Y.get_value() for x in q]
    assert r == [1]

def test_load_script_from_string(get_compiled_file):
    yp = YP()
    with open(get_compiled_file('geometricobjects.prolog'), 'r') as f:
        yp.load_script_from_string(f.read(), overwrite=False)
    Y = yp.variable()
    q = yp.query('horizontal', [
        yp.functor('seg', [
            yp.functor('point', [1, 1]),
            yp.functor('point', [2, Y])
        ])
    ])
    r = [Y.get_value() for x in q]
    assert r == [1]

def test_functor_arities():
    s = compile_prolog_from_string('''
    likes(A,B) :- person(A), person(B), friend(A,B).
    likes(A,B,C) :- person(A),person(B), person(C), friend(A,B), friend(A,C).
    likes(A,B) :- person(A), person(B), person(C), foe(A,C), foe(B,C).
    person(mike).
    person(joe).
    person(pete).
    person(zack).
    friend(mike,pete).
    friend(mike,joe).
    foe(joe,zack).
    foe(pete,zack).
    ''', TestContext)

    yp = YP()
    yp.load_script_from_string(s, overwrite=False)
    X = yp.variable()
    Y = yp.variable()
    q = yp.query('likes', [ X, Y ])
    r = [(to_python(X.get_value()), to_python(Y.get_value())) for x in q]
    assert set(r) == set(
        [ ('mike','pete'),
            ('mike','joe'),
            ('joe','pete'),
            ('joe','joe'),
            ('pete','pete'),
            ('pete','joe'),
        ])


