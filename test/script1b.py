#!/usr/bin/env python

# import sys
# from YP import *
# from Variable import *
# from Atom import *


def fact(arg1):
  for l1 in unify(arg1, atom("blue")):
    yield False

