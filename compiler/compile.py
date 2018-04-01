#!/usr/bin/env python

import sys
from antlr4 import *
from prologLexer import *
from prologParser import *
from YPPrologVisitor import *
from YPGenerator import *
import argparse

class CompilerApp:
    def __init__(self):
        parser = argparse.ArgumentParser(description="YP Prolog compiler")
        parser.add_argument('sourcefile',metavar='SOURCE',type=str, nargs='?',help='Prolog source file')
        parser.add_argument('-d','--debug',action='store_true',help='generate debug output')
        self.args = parser.parse_args()
    def _error(self,msg):
        sys.stderr.write('Error: '+msg+"\n")
    def _debug(self,*args):
        if self.args.debug:
            self.args.outfile.write('# ' + " ".join([str(a) for a in args]) + '\n')
    def run(self):
        self.args.outfile = sys.stdout
        if self.args.sourcefile == None or self.args.sourcefile == '-':
            inp = StdinStream()
        else:
            try:
                inp = FileStream(self.args.sourcefile,encoding='utf8')
            except IOError:
                self._error("Could not open input file '%s.'" % self.args.sourcefile)
                sys.exit(1)
        self._debug(self.args)
        lexer = prologLexer(inp)
        stream = CommonTokenStream(lexer)
        parser = prologParser(stream)
        tree = parser.program()
        visitor = YPPrologVisitor(self.args)
        program = visitor.visit(tree)
        compiler = YPPrologCompiler(self.args)
        code = compiler.compileProgram(program)
        generator = YPPythonCodeGenerator()
        pythoncode = generator.generate(code)
        print pythoncode

if __name__=="__main__":
    CompilerApp().run()


