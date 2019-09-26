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


import unittest
import sys
import os
import pathlib
from yldprolog.engine import YP
from yldprolog.engine import Atom
from yldprolog.engine import Answer
from yldprolog.engine import unify

_DATA_DIR = pathlib.Path(os.path.dirname(__file__)) / 'data'

class TestYP(unittest.TestCase):
    def setUp(self):
        pass

    def test_setup_yp(self):
        yp = YP()
        yp.assert_fact(yp.atom('cat'), [yp.atom('tom')])
        V1 = yp.variable()
        args = [V1]
        # q = yp.match_dynamic(yp.atom('cat'),args)
        q = yp.query('cat', args)
        r = [[v.get_value() for v in args] for r in q]
        self.assertEqual(r, [[yp.atom('tom')]])

    def test_clear(self):
        yp = YP()
        yp.assert_fact(yp.atom('cat'), [yp.atom('tom')])
        yp.clear()
        V1 = yp.variable()
        args = [V1]
        # q = yp.match_dynamic(yp.atom('cat'),args)
        q = yp.query('cat', args)
        r = [[v.get_value() for v in args] for r in q]
        self.assertEqual(r, [])


    def test_evaluate_bounded_projection_function(self):
        yp = YP()
        yp.assert_fact(yp.atom('cat'), [yp.atom('tom')])
        V1 = yp.variable()
        q = yp.query('cat', [V1])
        r = yp.evaluate_bounded(q, (lambda x: V1.get_value()))
        self.assertEqual(r, [yp.atom('tom')])

    def test_match_example_horizontal_vertical(self):
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

        self.assertEqual(r0, [False])
        self.assertEqual(r1, [])
        self.assertEqual(r2, [1])


    def test_match_answer_different_arity(self):
        yp = YP()
        a = Answer([yp.atom('tom')])
        r = list(a.match([yp.variable(), yp.variable()]))
        self.assertEqual(r, [])
    def test_match_answer_matching(self):
        yp = YP()
        a = Answer([yp.atom('tom')])
        v = yp.variable()
        r = [v.get_value() for x in a.match([v])]
        self.assertEqual(r, [yp.atom('tom')])
    def test_match_answer_not_matching(self):
        yp = YP()
        a = Answer([yp.atom('tom'), yp.atom('cat')])
        r = list(a.match([yp.atom('tom'), yp.atom('mouse')]))
        self.assertEqual(r, [])

    def test_unify_atoms_equal(self):
        yp = YP()
        a1 = yp.atom('tom')
        a2 = yp.atom('tom')
        r = list(unify(a1, a2))
        self.assertEqual(r, [False])

    def test_unify_atoms_different(self):
        yp = YP()
        a1 = yp.atom('tom')
        a2 = yp.atom('jerry')
        r = list(unify(a1, a2))
        self.assertEqual(r, [])

    def test_unify_variable_unbound(self):
        yp = YP()
        a1 = yp.atom('tom')
        v1 = yp.variable()
        r = [v1.get_value() for x in unify(v1, a1)]
        # self.assertEqual(r,[False])
        self.assertEqual(r, [yp.atom('tom')])

    def test_unify_variable_integer(self):
        yp = YP()
        v1 = yp.variable()
        r = [v1.get_value() for x in unify(v1, 5)]
        self.assertEqual(r, [5])

    def test_unify_variable_with_variable(self):
        yp = YP()
        v1 = yp.variable()
        v2 = yp.variable()
        r = [(v1.get_value(), v2.get_value()) for x in unify(v1, v2)]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][0], r[0][1])

    def test_unify_variable_complex_atom(self):
        yp = YP()
        a1 = yp.functor("point", [1, 1])
        v1 = yp.variable()
        r = [v1.get_value() for x in unify(v1, a1)]
        self.assertEqual(r, [a1])

    def test_unify_complex_atoms(self):
        yp = YP()
        v1 = yp.variable()
        v2 = yp.variable()
        a1 = yp.functor("point", [v1, 2])
        a2 = yp.functor("point", [1, v2])
        r = [(v1.get_value(), v2.get_value()) for x in unify(a1, a2)]
        self.assertEqual(r, [(1, 2)])

    def test_unify_complex_atoms_not_matching(self):
        yp = YP()
        v1 = yp.variable()
        a1 = yp.functor("point", [v1, 2])
        a2 = yp.functor("point", [1, 1])
        r = [v1.get_value() for x in unify(a1, a2)]
        self.assertEqual(r, [])

    def test_unify_complex_atoms_free_variable(self):
        yp = YP()
        v1 = yp.variable()
        v2 = yp.variable()
        a1 = yp.functor("point", [v1, 2])
        a2 = yp.functor("point", [v2, 2])
        r = [(v1.get_value(), v2.get_value()) for x in unify(a1, a2)]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][0], r[0][1])

    # lists
    def test_unify_lists(self):
        yp = YP()
        v1 = yp.variable()
        l1 = yp.listpair(yp.atom("a"), yp.listpair(yp.atom("b"), yp.ATOM_NIL))
        l2 = yp.listpair(yp.atom("a"), yp.listpair(v1, yp.ATOM_NIL))
        r = [v1.get_value() for x in unify(l1, l2)]
        self.assertEqual(r, [yp.atom("b")])

    def test_unify_lists_with_makelist(self):
        yp = YP()
        v1 = yp.variable()
        l1 = yp.listpair(yp.atom("a"), yp.listpair(yp.atom("b"), yp.ATOM_NIL))
        l2 = yp.makelist([yp.atom("a"), v1])
        r = [v1.get_value() for x in unify(l1, l2)]
        self.assertEqual(r, [yp.atom("b")])

    # test loading a script
    def test_load_monkey_and_banana_script(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'monkey.py')
        # canget(state(atdoor,onfloor,atwindow,hasnot))
        q = yp.query('canget', [yp.functor('state',
                [yp.atom('atdoor'), yp.atom('onfloor'),
                yp.atom('atwindow'), yp.atom('hasnot')])])
        # this query has infinitely many solutions, just get the first one
        self.assertEqual(next(q), False)


    # test concurrency when sourcing scripts
    def test_load_scripts_concurrently(self):
        yp1 = YP()
        yp2 = YP()
        yp1.load_script_from_file(_DATA_DIR / 'script1a.py')
        yp2.load_script_from_file(_DATA_DIR / 'script1b.py')
        X1 = yp1.variable()
        q1 = yp1.query('fact', [X1])
        X2 = yp2.variable()
        q2 = yp2.query('fact', [X2])
        r1 = [X1.get_value() for r in q1]
        r2 = [X2.get_value() for r in q2]
        self.assertNotEqual(r1, r2)

    # test concurrency when asserting facts
    def test_assert_facts_concurrently(self):
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
        self.assertNotEqual(r1, r2)

    # test implicit clauses with user defined functions
    def test_user_defined_function(self):
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
        self.assertEqual(side_effects, ['not blue'])

    def test_run_infinite_script(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'monkey.py')
        # canget(state(atdoor,onfloor,atwindow,hasnot))
        q = yp.query('canget', [yp.functor('state', [yp.atom('atdoor'),
            yp.atom('onfloor'), yp.atom('atwindow'), yp.atom('hasnot')])])
        # this query has infinitely many solutions, just get the first one
        recursion_limit = sys.getrecursionlimit()
        r = yp.evaluate_bounded(q, lambda x: x)
        self.assertEqual(sys.getrecursionlimit(), recursion_limit)
        self.assertGreaterEqual(len(r), 1)

    def test_run_lists_script(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'lists.py')
        l = yp.makelist([yp.atom(x) for x in ['Johnny', 'Dee Dee', 'Joey',
            'Tommy', 'Marky', 'Richie', 'Elvis', 'C. J.']])
        q = yp.query('member', [yp.atom('Richie'), l])
        r = list(q)
        self.assertEqual(r, [False])
        v1 = yp.variable()
        v2 = yp.variable()
        v3 = yp.variable()
        q = yp.query('testlist', [yp.makelist([v1, v2, v3])])
        r = [[v1.get_value(), v2.get_value(), v3.get_value()] for x in q]
        self.assertEqual(r, [[yp.atom('red'), yp.atom('green'), yp.atom('blue')]])

    def test_sploit_eval(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'eval.py')
        q = yp.query('sploit', ['1+1'])
        r = list(q)
        self.assertEqual(r, [])

    def test_load_scripts_add_multiple_definitions(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'defs1.py', overwrite=False)
        yp.load_script_from_file(_DATA_DIR / 'defs2.py', overwrite=False)
        v1 = yp.variable()
        v2 = yp.variable()
        v3 = yp.variable()
        q = yp.query('testlist', [yp.makelist([v1, v2, v3])])
        r = [(v1.get_value(), v2.get_value(), v3.get_value()) for x in q]
        self.assertEqual(set(r), set([
            (yp.atom('red'), yp.atom('green'), yp.atom('blue')),
            (yp.atom('cyan'), yp.atom('magenta'), yp.atom('yellow'))
        ]))

    def test_load_scripts_overwrite_multiple_definitions(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'defs1.py', overwrite=True)
        yp.load_script_from_file(_DATA_DIR / 'defs2.py', overwrite=True)
        v1 = yp.variable()
        v2 = yp.variable()
        v3 = yp.variable()
        q = yp.query('testlist', [yp.makelist([v1, v2, v3])])
        r = [(v1.get_value(), v2.get_value(), v3.get_value()) for x in q]
        self.assertEqual(set(r), set([
            (yp.atom('cyan'), yp.atom('magenta'), yp.atom('yellow'))
        ]))

    def test_query_without_predicates(self):
        yp = YP()
        v1 = yp.variable()
        q = yp.query('nonexistentpred', [v1])
        r = list(q)
        self.assertEqual(r, [])

    def test_load_scripts_with_dependencies_in_order(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'subscript.py', overwrite=False)
        yp.load_script_from_file(_DATA_DIR / 'mainscript.py', overwrite=False)
        v1 = yp.variable()
        q = yp.query('main', [v1])
        r = [v1.get_value() for x in q]
        self.assertEqual(r, [yp.atom('yes'), yp.atom('no'), yp.atom('maybe')])

    def test_load_scripts_with_dependencies_out_of_order(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'mainscript.py', overwrite=False)
        yp.load_script_from_file(_DATA_DIR / 'subscript.py', overwrite=False)
        v1 = yp.variable()
        q = yp.query('main', [v1])
        r = [v1.get_value() for x in q]
        self.assertEqual(r, [yp.atom('yes'), yp.atom('no'), yp.atom('maybe')])

    def test_load_clauses_with_functors(self):
        yp = YP()
        yp.load_script_from_file(_DATA_DIR / 'geometricobjects.py', overwrite=False)
        Y = yp.variable()
        q = yp.query('horizontal', [
            yp.functor('seg', [
                yp.functor('point', [1, 1]),
                yp.functor('point', [2, Y])
            ])
        ])
        r = [Y.get_value() for x in q]
        self.assertEqual(r, [1])

    def test_load_script_from_string(self):
        yp = YP()
        with open(_DATA_DIR / 'geometricobjects.py', 'r') as f:
            yp.load_script_from_string(f.read(), overwrite=False)
        Y = yp.variable()
        q = yp.query('horizontal', [
            yp.functor('seg', [
                yp.functor('point', [1, 1]),
                yp.functor('point', [2, Y])
            ])
        ])
        r = [Y.get_value() for x in q]
        self.assertEqual(r, [1])


if __name__ == "__main__":
    unittest.main()
