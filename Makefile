TEST_PROLOG_SOURCES=$(wildcard test/data/*.prolog)
TEST_PROLOG_TARGETS=$(TEST_PROLOG_SOURCES:.prolog=.py)

PROLOG_COMPILE=python -m yldprolog.compiler

.PHONY: test install dist

compiler: yldprolog/prologVisitor.py

yldprolog/prologVisitor.py: yldprolog/prolog.g4
	cd yldprolog && sh build.sh

test: $(TEST_PROLOG_TARGETS)
	python -m unittest discover -p test_*.py test

%.py: %.prolog
	${PROLOG_COMPILE} "$<" > "$@"

install: compiler
	python setup.py clean install

dist: compiler
	python setup.py sdist bdist_wheel

