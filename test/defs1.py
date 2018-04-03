def testlist(arg1):
  doBreak = False
  for _ in [1]:
    for l1 in unify(arg1,makelist([atom(u'red'),atom(u'green'),atom(u'blue')])):
      yield False
    if doBreak:
      break
  if False:
      yield False

