#!/usr/bin/env python

import sys
from antlr4 import *
from prologLexer import *
from prologParser import *
from YPPrologVisitor import *
from YPGenerator import *

def main(argv):
    inp = FileStream(argv[1])
    lexer = prologLexer(inp)
    stream = CommonTokenStream(lexer)
    parser = prologParser(stream)
    tree = parser.program()
    visitor = YPPrologVisitor()
    clauses = visitor.visit(tree)
    generator = YPGenerator()
    lines = generator.generate(clauses)
    print lines

if __name__=="__main__":
    main(sys.argv)


