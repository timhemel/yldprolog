#!/usr/bin/env python3
#
# yldprolog - a rewrite of Yield Prolog
#
# This file is part of yldprolog.
#
# yldprolog is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License,
# version 3, as published by the Free Software Foundation.
#
# yldprolog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License, version 3, along with BANG.  If not, see
# <http://www.gnu.org/licenses/>
#
# Copyright 2018-2019 - Tim Hemel
# Licensed under the terms of the GNU Affero General Public License
# version 3
# SPDX-License-Identifier: AGPL-3.0-only


import sys
import antlr4
from antlr4 import *
from .prologLexer import *
from .prologParser import *
from .YPPrologVisitor import *
from .YPGenerator import *
import argparse

class DefaultCompilerOptions:
    debug = False

def compile_prolog_from_stream(inp, options):
    lexer = prologLexer(inp)
    stream = CommonTokenStream(lexer)
    parser = prologParser(stream)
    tree = parser.program()
    visitor = YPPrologVisitor(options)
    program = visitor.visit(tree)
    compiler = YPPrologCompiler(options)
    code = compiler.compileProgram(program)
    generator = YPPythonCodeGenerator()
    pythoncode = generator.generate(code)
    return pythoncode


def compile_prolog_from_string(source, options=DefaultCompilerOptions):
    inp = antlr4.InputStream(source)
    return compile_prolog_from_stream(inp, options)

def compile_prolog_from_file(path, options=DefaultCompilerOptions):
    inp = FileStream(path, encoding='utf8')
    return compile_prolog_from_stream(inp, options)

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
        pythoncode = compile_prolog_from_stream(inp, self.args)
        self.args.outfile.write(pythoncode)

def main():
    CompilerApp().run()

if __name__=="__main__":
    main()



