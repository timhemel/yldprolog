#!/usr/bin/env python

# import sys
# from YP import *
# from Variable import *
# from Atom import *


def move(arg1, arg2, arg3):
  for l1 in unify(arg1, functor("state", [atom("middle"), atom("onbox"), atom("middle"), atom("hasnot")])):
    for l2 in unify(arg2, atom("grasp")):
      for l3 in unify(arg3, functor("state", [atom("middle"), atom("onbox"), atom("middle"), atom("has")])):
        yield False
  P = variable()
  H = variable()
  for l1 in unify(arg1, functor("state", [P, atom("onfloor"), P, H])):
    for l2 in unify(arg2, atom("climb")):
      for l3 in unify(arg3, functor("state", [P, atom("onbox"), P, H])):
        yield False
  P1 = variable()
  H = variable()
  P2 = variable()
  for l1 in unify(arg1, functor("state", [P1, atom("onfloor"), P1, H])):
    for l2 in unify(arg2, functor2("push", P1, P2)):
      for l3 in unify(arg3, functor("state", [P2, atom("onfloor"), P2, H])):
        yield False
  P1 = variable()
  B = variable()
  H = variable()
  P2 = variable()
  for l1 in unify(arg1, functor("state", [P1, atom("onfloor"), B, H])):
    for l2 in unify(arg2, functor2("walk", P1, P2)):
      for l3 in unify(arg3, functor("state", [P2, atom("onfloor"), B, H])):
        yield False

def canget(arg1):
  x1 = variable()
  x2 = variable()
  x3 = variable()
  for l1 in unify(arg1, functor("state", [x1, x2, x3, atom("has")])):
    yield False
  State1 = arg1
  Move = variable()
  State2 = variable()
  for l1 in move(State1, Move, State2):
    for l2 in canget(State2):
      yield False

