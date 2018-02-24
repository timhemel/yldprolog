#!/usr/bin/env python

import sys
import os
from YP import *
from Compiler2 import *

print """#!/usr/bin/env python

# import sys
# from YP import *
# from Variable import *
# from Atom import *

"""

#    prologCode = \
#        "uncle(Person, Uncle) :- \n" + \
#        "  parent(Person, Parent), \n" + \
#        "  brother(Parent, Uncle). \n"
YP.tell(sys.stdout)
#    YP.see(YP.StringReader(prologCode))
YP.see(sys.stdin)
TermList = Variable()
PseudoCode = Variable()
for l1 in parseInput(TermList):
        # print >>sys.stderr, TermList
	for l2 in makeFunctionPseudoCode(TermList, PseudoCode):
                # print >>sys.stderr, '-->', PseudoCode
		convertFunctionPython(PseudoCode)
	YP.seen()

