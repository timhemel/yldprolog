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
        yp.assertFact(yp.atom('cat'),yp.atom('tom'))
        V1 = Variable()
        args = [V1]
        q = yp.matchDynamic(yp.atom('cat'),args)
        r = [ [ v.getValue() for v in args ] for r in q ]
        self.assertEquals(r, [ [yp.atom('tom')] ])
    def testMatchAnswerDifferentArity(self):
        yp = YP()
        a = Answer([yp.atom('tom')])
        r = [x for x in a.match([Variable(), Variable()])]
        self.assertEquals(r,[])
    def testMatchAnswerMatching(self):
        yp = YP()
        a = Answer([yp.atom('tom')])
        v = Variable()
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
        v1 = Variable()
        r = [ v1.getValue() for x in unify(v1,a1) ]
        # self.assertEquals(r,[False])
        self.assertEquals(r,[yp.atom('tom')])


if __name__=="__main__":
    unittest.main()


