# YieldProlog rewrite

It is very difficult to run multiple engines concurrently in YieldProlog, as all the predicates are stored in a class at the module level. To have multiple engines would mean to import the YP module under a different name.

This rewrite creates the engine but stores all predicates in an object instance. That way it is possible to use multiple engines simultaneously. The interface for queries was changed and as a result, the code generated by the existing YieldProlog compiler does not work with the new interface. Some small changes to the YieldProlog compiler fix this.

# Example

```
TODO
```

You can compile this script with:

```
compiler/YieldProlog/plcompile.py < script.prolog > script.py
```

