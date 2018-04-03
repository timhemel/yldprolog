def vertical(arg1):
  doBreak = False
  for _ in [1]:
    Y = variable()
    X = variable()
    Y1 = variable()
    for l1 in unify(arg1,functor(u'seg',[functor(u'point',[X,Y]),functor(u'point',[X,Y1])])):
      yield False
    if doBreak:
      break
  if False:
      yield False

def horizontal(arg1):
  doBreak = False
  for _ in [1]:
    Y = variable()
    X = variable()
    X1 = variable()
    for l1 in unify(arg1,functor(u'seg',[functor(u'point',[X,Y]),functor(u'point',[X1,Y])])):
      yield False
    if doBreak:
      break
  if False:
      yield False

