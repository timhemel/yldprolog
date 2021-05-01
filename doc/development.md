# Developing on yldprolog

## Building the compiler

### Installing ANTLR

You can use `antlr4` to build the prolog compiler. You will need version 4.9.1 or higher.

#### Installing ANTLR manually (optional)

If your system's antlr4 is older, you can download the ANTLR jar file from
the antlr web page:

```
wget https://www.antlr.org/download/antlr-4.9.1-complete.jar
```

Save this file somewhere, and create a wrapper script:

```
#!/bin/bash

java -cp "$HOME/antlr-4.7.2/antlr-4.7.2-complete.jar:$CLASSPATH" \
	org.antlr.v4.Tool "$@"
```

#### Installing the ANTLR Python runtime

You will also need to install the Python runtime, for example (Python3):

```
pip3 install antlr4-python3-runtime==4.7.2
```

#### Generating the compiler

You build the compiler by:
 
```
cd src/yldprolog
sh build.sh
```

This script assumes that there is an executable `antlr4` in your `PATH`.

