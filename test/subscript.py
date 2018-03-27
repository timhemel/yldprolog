#!/usr/bin/env python

# import sys
# from YP import *
# from Variable import *
# from Atom import *


def sub(P):
  for l1 in fact(P):
    yield False

def fact(arg1):
  for l1 in unify(arg1, atom("yes")):
    yield False
  for l1 in unify(arg1, atom("no")):
    yield False
  for l1 in unify(arg1, atom("maybe")):
    yield False

