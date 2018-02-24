#!/usr/bin/env python

# import sys
# from YP import *
# from Variable import *
# from Atom import *


def empty(arg1):
  for l1 in unify(arg1, Atom.NIL):
    yield False

def member(X, arg2):
  Tail = variable()
  for l1 in unify(arg2, listpair(X, Tail)):
    yield False
  Head = variable()
  Tail = variable()
  for l1 in unify(arg2, listpair(Head, Tail)):
    for l2 in member(X, Tail):
      yield False

def testlist(arg1):
  for l1 in unify(arg1, makelist([atom("red"), atom("green"), atom("blue")])):
    yield False

