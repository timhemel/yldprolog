# yldprolog Architecture

yldprolog in its core consists of two components: a compiler and an engine. The compiler
translates Prolog code into Python code that the engine can work with.

## Compiler

yldprolog supports a limited subset of Prolog's syntax. The compiler is static, i.e. you cannot
(re)define operators dynamically as you can in most Prolog implementations.


## Engine

Based on [Yield Prolog](http://yieldprolog.sourceforge.net/), queries in yldprolog will look
for generator functions (i.e. functions using `yield`). The generator will try to unify its
arguments and other variables with certain values, and iterate over the result. For every
successful unification, it will `yield` a value (the value does not matter, but the convention
is to `yield False`). The [Yield Prolog tutorial](http://yieldprolog.sourceforge.net/tutorial_toc.html)
explains how and why this works.

yldprolog defines two iterators already: `YPSuccess`, which yields a result and then stops, and `YPFail`,
which always stops.

Arguments to the generators have to be values in the Prolog world, i.e. an `Atom`, `Variable` or `Functor`.
Use the method `to_python` to get values in the Python world.

For unification, yldprolog provides the functions `unify` and (rarely needed) `unify_arrays`.

A variable can be bound to a value or not. To get its value, use `get_value`.

With this, you can call Python from the Prolog world. As a non-trivial example, the file `xpath.py` in `examples/xpath` shows
how to execute XPath queries from Prolog.

