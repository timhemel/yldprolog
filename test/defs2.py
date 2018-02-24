#!/usr/bin/env python

# import sys
# from YP import *
# from Variable import *
# from Atom import *


def testlist(arg1):
  for l1 in unify(arg1, makelist([atom("cyan"), atom("magenta"), atom("yellow")])):
    yield False

