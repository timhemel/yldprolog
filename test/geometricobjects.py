#!/usr/bin/env python

# import sys
# from YP import *
# from Variable import *
# from Atom import *


def horizontal(arg1):
  X = variable()
  Y = variable()
  X1 = variable()
  for l1 in unify(arg1, functor2("seg", functor2("point", X, Y), functor2("point", X1, Y))):
    yield False

def vertical(arg1):
  X = variable()
  Y = variable()
  Y1 = variable()
  for l1 in unify(arg1, functor2("seg", functor2("point", X, Y), functor2("point", X, Y1))):
    yield False

