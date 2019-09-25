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

import unittest
import re
import pathlib
import sys
import os
import yldprolog.compiler

_DATA_DIR = pathlib.Path(os.path.dirname(__file__)) / 'data'

def strip_comments(s):
    return re.sub(r'^#.*$', '', s, flags=re.MULTILINE).strip()

class TestYldPrologCompiler(unittest.TestCase):
    def setUp(self):
        pass

    def test_compile_empty_string(self):
        s = yldprolog.compiler.compile_prolog_from_string("")
        self.assertEqual(strip_comments(s), "")

    def test_compile_simple_string(self):
        s = yldprolog.compiler.compile_prolog_from_string(
                "testlist([cyan,magenta,yellow]).")
        self.assertRegex(strip_comments(s), r'testlist')

    def test_compile_from_file(self):
        path = _DATA_DIR / 'script1a.prolog'
        s = yldprolog.compiler.compile_prolog_from_file(path)
        self.assertRegex(strip_comments(s), r'red')


if __name__ == "__main__":
    unittest.main()
