#!/bin/sh

GRAMMAR=prolog

rm -f ${GRAMMAR}Lexer.py ${GRAMMAR}Lexer.tokens ${GRAMMAR}Listener.py ${GRAMMAR}Parser.py ${GRAMMAR}.tokens ${GRAMMAR}Visitor.py

antlr4 -Dlanguage=Python2 -visitor ${GRAMMAR}.g4

