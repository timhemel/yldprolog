def empty(arg1):
  doBreak = False
  for _ in [1]:
    for l1 in unify(arg1,ATOM_NIL):
      yield False
    if doBreak:
      break
  if False:
      yield False

def testlist(arg1):
  doBreak = False
  for _ in [1]:
    for l1 in unify(arg1,makelist([atom(u'red'),atom(u'green'),atom(u'blue')])):
      yield False
    if doBreak:
      break
  if False:
      yield False

def member(arg1,arg2):
  doBreak = False
  for _ in [1]:
    X = arg1
    Tail = variable()
    for l1 in unify(arg2,listpair(X,Tail)):
      yield False
    if doBreak:
      break
    X = arg1
    Head = variable()
    Tail = variable()
    for l1 in unify(arg2,listpair(Head,Tail)):
      for l2 in query(u'member',[X,Tail]):
        yield False
      if doBreak:
        break
    if doBreak:
      break
  if False:
      yield False

