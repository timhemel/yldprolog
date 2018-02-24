#!/usr/bin/env python

import unittest
import sys
sys.path.insert(0,'..')

from YP import YP
from YP import Atom
from YP import Variable
from YP import Answer
from YP import unify

class TestYP(unittest.TestCase):
    def setUp(self):
        pass
    def testSetupYP(self):
        yp = YP()
        yp.assertFact(yp.atom('cat'),[yp.atom('tom')])
        V1 = yp.variable()
        args = [V1]
        # q = yp.matchDynamic(yp.atom('cat'),args)
        q = yp.query('cat',args)
        r = [ [ v.getValue() for v in args ] for r in q ]
        self.assertEquals(r, [ [yp.atom('tom')] ])

    def testMatchExampleHorizontalVertical(self):
        yp = YP()
        X = yp.variable()
        Y = yp.variable()
        X1 = yp.variable()
        Y1 = yp.variable()
        # vertical(seg(point(X,Y),point(X,Y1))).
        yp.assertFact(yp.atom('vertical'), [
            yp.functor('seg', [
                yp.functor('point',[X,Y]),
                yp.functor('point',[X,Y1])
            ])
        ])
        # horizontal(seg(point(X,Y),point(X1,Y))).
        yp.assertFact(yp.atom('horizontal'), [
            yp.functor('seg', [
                yp.functor('point',[X,Y]),
                yp.functor('point',[X1,Y])
            ])
        ])

        # q0 = yp.matchDynamic(yp.atom('vertical'), [
        q0 = yp.query('vertical', [
            yp.functor('seg', [
                yp.functor('point',[1,1]),
                yp.functor('point',[1,2])
            ])
        ])

        # q1 = yp.matchDynamic(yp.atom('vertical'), [
        q1 = yp.query('vertical', [
            yp.functor('seg', [
                yp.functor('point',[1,1]),
                yp.functor('point',[2,Y])
            ])
        ])

        # q2 = yp.matchDynamic(yp.atom('horizontal'), [
        q2 = yp.query('horizontal', [
            yp.functor('seg', [
                yp.functor('point',[1,1]),
                yp.functor('point',[2,Y])
            ])
        ])
                
        r0 = [ r for r in q0 ]
        r1 = [ r for r in q1 ]
        r2 = [ Y.getValue() for r in q2 ]

        self.assertEquals(r0,[False])
        self.assertEquals(r1,[])
        self.assertEquals(r2,[1])


    def testMatchAnswerDifferentArity(self):
        yp = YP()
        a = Answer([yp.atom('tom')])
        r = [x for x in a.match([yp.variable(), yp.variable()])]
        self.assertEquals(r,[])
    def testMatchAnswerMatching(self):
        yp = YP()
        a = Answer([yp.atom('tom')])
        v = yp.variable()
        r = [v.getValue() for x in a.match([v])]
        self.assertEquals(r,[yp.atom('tom')])
    def testMatchAnswerNotMatching(self):
        yp = YP()
        a = Answer([yp.atom('tom'),yp.atom('cat')])
        r = [x for x in a.match([yp.atom('tom'),yp.atom('mouse')])]
        self.assertEquals(r,[])



    def testUnifyAtomsEqual(self):
        yp = YP()
        a1 = yp.atom('tom')
        a2 = yp.atom('tom')
        r = [ r for r in unify(a1,a2) ]
        self.assertEquals(r,[False])
    def testUnifyAtomsDifferent(self):
        yp = YP()
        a1 = yp.atom('tom')
        a2 = yp.atom('jerry')
        r = [ r for r in unify(a1,a2) ]
        self.assertEquals(r,[])
    def testUnifyVariableUnbound(self):
        yp = YP()
        a1 = yp.atom('tom')
        v1 = yp.variable()
        r = [ v1.getValue() for x in unify(v1,a1) ]
        # self.assertEquals(r,[False])
        self.assertEquals(r,[yp.atom('tom')])
    def testUnifyVariableInteger(self):
        yp = YP()
        v1 = yp.variable()
        r = [ v1.getValue() for x in unify(v1,5) ]
        self.assertEquals(r,[5])
    def testUnifyVariableWithVariable(self):
        yp = YP()
        v1 = yp.variable()
        v2 = yp.variable()
        r = [ (v1.getValue(),v2.getValue()) for x in unify(v1,v2) ]
        self.assertEquals(len(r),1)
        self.assertEquals(r[0][0],r[0][1])
    def testUnifyVariableComplexAtom(self):
        yp = YP()
        a1 = yp.functor("point",[1,1])
        v1 = yp.variable()
        r = [ v1.getValue() for x in unify(v1,a1) ]
        self.assertEquals(r,[a1])
    def testUnifyComplexAtoms(self):
        yp = YP()
        v1 = yp.variable()
        v2 = yp.variable()
        a1 = yp.functor("point",[v1,2])
        a2 = yp.functor("point",[1,v2])
        r = [ (v1.getValue(),v2.getValue()) for x in unify(a1,a2) ]
        self.assertEquals(r,[(1,2)])
    def testUnifyComplexAtomsNotMatching(self):
        yp = YP()
        v1 = yp.variable()
        a1 = yp.functor("point",[v1,2])
        a2 = yp.functor("point",[1,1])
        r = [ v1.getValue() for x in unify(a1,a2) ]
        self.assertEquals(r,[])
    def testUnifyComplexAtomsFreeVariable(self):
        yp = YP()
        v1 = yp.variable()
        v2 = yp.variable()
        a1 = yp.functor("point",[v1,2])
        a2 = yp.functor("point",[v2,2])
        r = [ (v1.getValue(),v2.getValue()) for x in unify(a1,a2) ]
        self.assertEquals(len(r),1)
        self.assertEquals(r[0][0],r[0][1])

    # lists
    def testUnifyLists(self):
        yp = YP()
        v1 = yp.variable()
        l1 = yp.listpair(yp.atom("a"), yp.listpair(yp.atom("b"),yp.ATOM_NIL))
        l2 = yp.listpair(yp.atom("a"), yp.listpair(v1,yp.ATOM_NIL))
        r = [ v1.getValue() for x in unify(l1,l2) ]
        self.assertEquals(r,[yp.atom("b")])

    def testUnifyListsWithMakelist(self):
        yp = YP()
        v1 = yp.variable()
        l1 = yp.listpair(yp.atom("a"), yp.listpair(yp.atom("b"),yp.ATOM_NIL))
        l2 = yp.makelist([yp.atom("a"),v1])
        r = [ v1.getValue() for x in unify(l1,l2) ]
        self.assertEquals(r,[yp.atom("b")])

    # test loading a script
    def testLoadMonkeyAndBananaScript(self):
        yp = YP()
        yp.loadScript('monkey.py')
        # canget(state(atdoor,onfloor,atwindow,hasnot))
        q = yp.query('canget',[ yp.functor('state',[yp.atom('atdoor'),yp.atom('onfloor'),yp.atom('atwindow'),yp.atom('hasnot')])])
        # this query has infinitely many solutions, just get the first one
        self.assertEquals(q.next(),False)


    # test concurrency when sourcing scripts
    def testLoadScriptsConcurrently(self):
        yp1 = YP()
        yp2 = YP()
        yp1.loadScript('script1a.py')
        yp2.loadScript('script1b.py')
        X1 = yp1.variable()
        q1 = yp1.query('fact',[X1])
        X2 = yp2.variable()
        q2 = yp2.query('fact',[X2])
        r1 = [ X1.getValue() for r in q1 ]
        r2 = [ X2.getValue() for r in q2 ]
        self.assertNotEquals(r1,r2)

    # test concurrency when asserting facts
    def testAssertFactsConcurrently(self):
        yp1 = YP()
        yp2 = YP()
        yp1.assertFact(yp1.atom('fact'), [yp1.atom('red')])
        yp2.assertFact(yp2.atom('fact'), [yp2.atom('blue')])
        X1 = yp1.variable()
        q1 = yp1.query('fact',[X1])
        X2 = yp2.variable()
        q2 = yp2.query('fact',[X2])
        r1 = [ X1.getValue() for r in q1 ]
        r2 = [ X2.getValue() for r in q2 ]
        self.assertNotEquals(r1,r2)

    # test implicit clauses with user defined functions
    def testUserDefinedFunction(self):
        yp = YP()
        side_effects = []
        def func(arg1):
            # check if arg1 instantiated
            if isinstance(arg1,Atom) and arg1.name() != "blue":
                side_effects.append('not blue')
            for l1 in unify(arg1, yp.atom("blue")):
                yield False
        yp.registerFunction('func',func)
        q = yp.query('func',[yp.atom('red')])
        r = [ x for x in q ]
        self.assertEquals(side_effects, ['not blue'])



    def testRunInfiniteScript(self):
        yp = YP()
        yp.loadScript('monkey.py')
        # canget(state(atdoor,onfloor,atwindow,hasnot))
        q = yp.query('canget',[ yp.functor('state',[yp.atom('atdoor'),yp.atom('onfloor'),yp.atom('atwindow'),yp.atom('hasnot')])])
        # this query has infinitely many solutions, just get the first one
        recursion_limit = sys.getrecursionlimit()
        r = yp.evaluateBounded(q, lambda x:x)
        self.assertEquals(sys.getrecursionlimit(),recursion_limit)
        self.assertGreaterEqual(len(r),1)

    def testRunListsScript(self):
        yp = YP()
        yp.loadScript('lists.py')
        l = yp.makelist([yp.atom(x) for x in ['Johnny','Dee Dee','Joey','Tommy','Marky','Richie','Elvis','C. J.']])
        q = yp.query('member',[ yp.atom('Richie'), l ])
        r = [ x for x in q ]
        self.assertEquals(r,[False])
        v1 = yp.variable()
        v2 = yp.variable()
        v3 = yp.variable()
        q = yp.query('testlist', [yp.makelist([v1,v2,v3])])
        r = [ [v1.getValue(),v2.getValue(),v3.getValue()] for x in q ]
        self.assertEqual(r,[[yp.atom('red'),yp.atom('green'),yp.atom('blue')]])

if __name__=="__main__":
    unittest.main()


