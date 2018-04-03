def sub(arg1):
  doBreak = False
  for _ in [1]:
    P = arg1
    for l1 in query(u'fact',[P]):
      yield False
    if doBreak:
      break
  if False:
      yield False

def fact(arg1):
  doBreak = False
  for _ in [1]:
    for l1 in unify(arg1,atom(u'yes')):
      yield False
    if doBreak:
      break
    for l1 in unify(arg1,atom(u'no')):
      yield False
    if doBreak:
      break
    for l1 in unify(arg1,atom(u'maybe')):
      yield False
    if doBreak:
      break
  if False:
      yield False

