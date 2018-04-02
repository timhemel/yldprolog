# COMPILE=../compiler/YieldProlog/plcompile.py
COMPILE=../compiler/compile.py

SOURCES=$(wildcard *.prolog)
TARGETS=$(SOURCES:.prolog=.py)


%.py: %.prolog
	${COMPILE} < "$<" > "$@"

all: $(TARGETS)
