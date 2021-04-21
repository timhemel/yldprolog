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
import contextlib
import click

def compile_prolog_from_stream(inp, ctx):
    lexer = prologLexer(inp)
    stream = CommonTokenStream(lexer)
    parser = prologParser(stream)
    tree = parser.program()
    visitor = YPPrologVisitor(ctx)
    program = visitor.visit(tree)
    compiler = YPPrologCompiler(ctx)
    code = compiler.compileProgram(program)
    generator = YPPythonCodeGenerator(ctx)
    pythoncode = generator.generate(code)
    return pythoncode

@contextlib.contextmanager
def open_input_file(fn):
    if fn == '-':
        inf = StdinStream()
    else:
        inf = FileStream(fn, encoding='utf8')
    try:
        yield inf
    finally:
        del inf

@contextlib.contextmanager
def open_output_file(fn):
    if fn == '-':
        outf = sys.stdout
    else:
        outf = open(fn,'w')
    try:
        yield outf
    finally:
        outf.close()

def set_debug_options(ctx):
    ctx.debug_parser = ctx.params['debug_parser']
    ctx.debug_generator = ctx.params['debug_generator']
    ctx.debug_filename = ctx.params['debug_filename']
    if ctx.params['debug']:
        ctx.debug_parser = True
        ctx.debug_generator = True
        ctx.debug_filename = True


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-d','--debug',is_flag=True)
@click.option('-o','--outfile',type=click.Path(allow_dash=True), default='-')
@click.option('--debug-parser', is_flag=True, default=False)
@click.option('--debug-generator', is_flag=True, default=False)
@click.option('--debug-filename', is_flag=True, default=False)
@click.argument('source', nargs=-1, type=click.Path(exists=True,file_okay=True,dir_okay=False,readable=True,allow_dash=True))
@click.pass_context
def main(ctx, source, outfile, debug, debug_parser, debug_generator, debug_filename):

    set_debug_options(ctx)

    with open_output_file(outfile) as outf:
        ctx.outf = outf
        # TODO: multiple source files
        for s in source:
            ctx.current_source_file = s
            with open_input_file(s) as inf:
                pythoncode = compile_prolog_from_stream(inf, ctx)
                outf.write(pythoncode)

if __name__=="__main__":
    main()



