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
# License, version 3, along with yldprolog.  If not, see
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
from .yp_prolog_visitor import *
from .yp_generator import *
import contextlib
import click
from .errors import CompilerError

def _compile_prolog_from_stream(inp, ctx):
    '''compiles prolog source from an antlr4 stream.'''
    lexer = prologLexer(inp)
    stream = CommonTokenStream(lexer)
    parser = prologParser(stream)
    tree = parser.program()
    visitor = YPPrologVisitor(ctx)
    program = visitor.visit(tree)
    compiler = YPPrologCompiler(ctx)
    code = compiler.compile_program(program)
    generator = YPPythonCodeGenerator(ctx)
    pythoncode = generator.generate(code)
    return pythoncode

class CompilerContext:
    '''This class defines properties that affect the behaviour of the
    compiler.

    General options:
    ----------------

    current_source_file: filename of the input source. Used in error messages
                         and debug output.

    Debugging options:
    ------------------

    debug_filename:  show the filename in the generated code.
    debug_parser:    enable debug output for the parser (visitor).
    debug_generator: enable debug output for the code generator.
    outf:            output file object
    '''

    debug_filename = ''
    debug_parser = False
    debug_generator = False
    current_source_file = ''
    outf = None

def compile_prolog_from_string(source, options=CompilerContext):
    '''compiles prolog from the string source. options is an object or class
    that defines the properties as specified in CompilerContext.'''
    inp = antlr4.InputStream(source)
    return _compile_prolog_from_stream(inp, options)

def compile_prolog_from_file(path, options=CompilerContext):
    '''compiles prolog from the string source. options is an object or class
    that defines the properties as specified in CompilerContext.'''
    inp = FileStream(path, encoding='utf8')
    return _compile_prolog_from_stream(inp, options)

@contextlib.contextmanager
def _open_input_file(fn):
    if fn == '-':
        inf = StdinStream()
    else:
        inf = FileStream(fn, encoding='utf8')
    try:
        yield inf
    finally:
        del inf

@contextlib.contextmanager
def _open_output_file(fn):
    if fn == '-':
        outf = sys.stdout
    else:
        outf = open(fn,'w')
    try:
        yield outf
    finally:
        outf.close()

def _set_debug_options(ctx):
    ctx.debug_parser = ctx.params['debug_parser']
    ctx.debug_generator = ctx.params['debug_generator']
    ctx.debug_filename = ctx.params['debug_filename']
    if ctx.params['debug']:
        ctx.debug_parser = True
        ctx.debug_generator = True
        ctx.debug_filename = True


_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=_CONTEXT_SETTINGS)
@click.option('-d','--debug',is_flag=True)
@click.option('-o','--outfile',type=click.Path(allow_dash=True), default='-')
@click.option('--debug-parser', is_flag=True, default=False)
@click.option('--debug-generator', is_flag=True, default=False)
@click.option('--debug-filename', is_flag=True, default=False)
@click.argument('source', nargs=-1, type=click.Path(exists=True,file_okay=True,dir_okay=False,readable=True,allow_dash=True))
@click.pass_context
def main(ctx, source, outfile, debug, debug_parser, debug_generator, debug_filename):
    """Run the compiler CLI."""

    _set_debug_options(ctx)

    with _open_output_file(outfile) as outf:
        ctx.outf = outf
        for s in source:
            ctx.current_source_file = s
            with _open_input_file(s) as inf:
                try:
                    pythoncode = _compile_prolog_from_stream(inf, ctx)
                    outf.write(pythoncode)
                except CompilerError as e:
                    raise click.ClickException(str(e)) from e

if __name__=="__main__":
    main()



