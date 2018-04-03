def testlist(arg1):
  doBreak = False
  for _ in [1]:
    for l1 in unify(arg1,makelist([atom(u'cyan'),atom(u'magenta'),atom(u'yellow')])):
      yield False
    if doBreak:
      break
  if False:
      yield False

