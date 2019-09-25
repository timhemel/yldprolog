
.PHONY: test install

compiler: yldprolog/prologVisitor.py

yldprolog/prologVisitor.py: yldprolog/prolog.g4
	cd yldprolog && sh build.sh

test:
	python -m unittest discover -p test_*.py test

install: compiler
	python setup.py install

