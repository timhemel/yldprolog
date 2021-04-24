# yldprolog

yldprolog is a rewrite of [YieldProlog](http://yieldprolog.sourceforge.net/), which compiles Prolog into source code that you can embed in your code. Yield Prolog supports several programming languages, yldprolog only supports Python.

The rewrite grew out of the need to run multiple Prolog instances concurrently. In Yield Prolog, the active instance is a Python module, and therefore it is cumbersome to have multiple instances at the same time. This rewrite uses object instances instead, which make this much easier.

The interface for the engine changed and as a result, the code generated by the existing YieldProlog compiler is not compatible with yldprolog. You will need to use the yldprolog compiler.

The yldprolog compiler uses ANTLR and supports the most common Prolog constructs.

# Usage

## Compiling a Prolog program

Let's look at the following Prolog script:

```
%
% The following Prolog code is based on the example "monkey and banana"
% from: Ivan Bratko, Prolog Programming for Artificial Intelligence,
% third edition. ISBN 0-201-40375-7.
%

move(state(middle,onbox,middle,hasnot),
     grasp,
     state(middle,onbox,middle,has)).

move(state(P,onfloor,P,H),
     climb,
     state(P,onbox,P,H)).

move(state(P1,onfloor,P1,H),
     push(P1,P2),
     state(P2,onfloor,P2,H)).

move(state(P1,onfloor,B,H),
     walk(P1,P2),
     state(P2,onfloor,B,H)).

canget(state(_,_,_,has)).
canget(State1) :-
     move(State1,Move,State2),
     canget(State2).
```

You can compile this Prolog script with:

```
yldpc monkey.prolog > monkey.py
```

The result is a Python module that defines the predicates as functions.
You can use these modules in your program, for example.

```
# 1. construct the yldproglog engine
yp = YP()
# 2. load a script from a path or filename
yp.load_script_from_file(pathlib.Path(_SCRIPT_DIR) / 'monkey.py')
# 3. execute the query:
#    canget(state(atdoor, onfloor, atwindow, hasnot))
q = yp.query('canget', [yp.functor('state',
	[yp.atom('atdoor'), yp.atom('onfloor'),
	yp.atom('atwindow'), yp.atom('hasnot')])])
# 4. q is a generator that will give all solutions. Since this
#    query has infinitely many solutions, we will just get the
#    first one.
self.assertEqual(next(q), False)
```

# Building the compiler

## Installing ANTLR

You can use `antlr4` to build the prolog compiler. You will need version 4.7.2 or higher.

### Installing ANTLR manually (optional)

If your system's antlr4 is older, you can download the ANTLR jar file from
the antlr web page:

```
wget https://www.antlr.org/download/antlr-4.7.2-complete.jar
```

Save this file somewhere, and create a wrapper script:

```
#!/bin/bash

java -cp "$HOME/antlr-4.7.2/antlr-4.7.2-complete.jar:$CLASSPATH" \
	org.antlr.v4.Tool "$@"
```

### Installing the ANTLR Python runtime

You will also need to install the Python runtime, for example (Python3):

```
pip3 install antlr4-python3-runtime==4.7.2
```

### Generating the compiler

You build the compiler by running `make compiler`.
 

