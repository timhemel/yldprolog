def canget(arg1):
  doBreak = False
  for _ in [1]:
    x2 = variable()
    x3 = variable()
    x1 = variable()
    for l1 in unify(arg1,functor(u'state',[x1,x2,x3,atom(u'has')])):
      yield False
    if doBreak:
      break
    State1 = arg1
    State2 = variable()
    Move = variable()
    for l1 in query(u'move',[State1,Move,State2]):
      for l2 in query(u'canget',[State2]):
        yield False
      if doBreak:
        break
    if doBreak:
      break
  if False:
      yield False

def move(arg1,arg2,arg3):
  doBreak = False
  for _ in [1]:
    for l1 in unify(arg1,functor(u'state',[atom(u'middle'),atom(u'onbox'),atom(u'middle'),atom(u'hasnot')])):
      for l2 in unify(arg2,atom(u'grasp')):
        for l3 in unify(arg3,functor(u'state',[atom(u'middle'),atom(u'onbox'),atom(u'middle'),atom(u'has')])):
          yield False
        if doBreak:
          break
      if doBreak:
        break
    if doBreak:
      break
    P = variable()
    H = variable()
    for l1 in unify(arg1,functor(u'state',[P,atom(u'onfloor'),P,H])):
      for l2 in unify(arg2,atom(u'climb')):
        for l3 in unify(arg3,functor(u'state',[P,atom(u'onbox'),P,H])):
          yield False
        if doBreak:
          break
      if doBreak:
        break
    if doBreak:
      break
    P2 = variable()
    H = variable()
    P1 = variable()
    for l1 in unify(arg1,functor(u'state',[P1,atom(u'onfloor'),P1,H])):
      for l2 in unify(arg2,functor(u'push',[P1,P2])):
        for l3 in unify(arg3,functor(u'state',[P2,atom(u'onfloor'),P2,H])):
          yield False
        if doBreak:
          break
      if doBreak:
        break
    if doBreak:
      break
    P2 = variable()
    H = variable()
    B = variable()
    P1 = variable()
    for l1 in unify(arg1,functor(u'state',[P1,atom(u'onfloor'),B,H])):
      for l2 in unify(arg2,functor(u'walk',[P1,P2])):
        for l3 in unify(arg3,functor(u'state',[P2,atom(u'onfloor'),B,H])):
          yield False
        if doBreak:
          break
      if doBreak:
        break
    if doBreak:
      break
  if False:
      yield False

