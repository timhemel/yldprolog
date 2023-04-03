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

import pytest
import re
import pathlib
import sys
import os
import yldprolog.compiler

_DATA_DIR = pathlib.Path(os.path.dirname(__file__)) / 'data'

class TestContext:
    debug_filename = ''
    debug_parser = False
    debug_generator = False

def strip_comments(s):
    return re.sub(r'^#.*$', '', s, flags=re.MULTILINE).strip()

def test_compile_empty_string():
    s = yldprolog.compiler.compile_prolog_from_string("", TestContext)
    assert strip_comments(s) ==  ''

def test_compile_simple_string():
    s = yldprolog.compiler.compile_prolog_from_string(
            "testlist([cyan,magenta,yellow]).", TestContext)
    assert re.search(r'testlist', strip_comments(s))

def test_compile_from_file():
    path = _DATA_DIR / 'script1a.prolog'
    s = yldprolog.compiler.compile_prolog_from_file(path, TestContext)
    assert re.search(r'red', strip_comments(s))

def test_compile_clause():
    s = yldprolog.compiler.compile_prolog_from_string(
            "member(X,[Y|L]) :- member(X,L).", TestContext)
    assert re.search(r'member',s)

def test_compile_syntax_error():
    with pytest.raises(Exception):
        s = yldprolog.compiler.compile_prolog_from_string(
            "member(X,[Y|L] :- member(X,L).", TestContext)

def test_compile_binary_operator_gt():
    s = yldprolog.compiler.compile_prolog_from_string(
            "gt(X,Y) :- X > Y.", TestContext)
    assert re.search(r'gt',s)

def test_compile_binary_operator_neq():
    s = yldprolog.compiler.compile_prolog_from_string(
            'neq(X,Y) :- X \\= Y.', TestContext)
    assert re.search(r'\\=',s)

def test_compile_expression_in_parentheses():
    s = yldprolog.compiler.compile_prolog_from_string(
            'neq(X,Y) :- (X \\= Y).', TestContext)
    assert re.search(r'\\=',s)


def test_compile_functor_arity():
    s = yldprolog.compiler.compile_prolog_from_string('''
    likes(A,B) :- person(A), person(B), friend(A,B).
    likes(A,B,C) :- person(A),person(B), person(C), friend(A,B), friend(A,C).
    ''', TestContext)
    assert re.search(r'def likes_2\(',s)
    assert re.search(r'def likes_3\(',s)

