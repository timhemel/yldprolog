/*
BSD License

Copyright (c) 2013, Tom Everett
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of Tom Everett nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

grammar prolog;

program 
    : clauselist // query?
    ;

clauselist 
    :  (clause|directive)*
    ;

clause 
    : (simplepredicate '.')
    | (simplepredicate ':-' predicateterm '.')
    ;

directive
    : ':-' simplepredicate '.' ;

predicatelist 
    :  predicateterm
    // :  predicateterm | predicateterm ',' predicatelist
    ;

simplepredicate 
    : TRUE
    | FAIL
    | CUT
    // | atom
    | functor
    ;

// TODO: atoms (functors with arity 0?)
functor
    : atom
    | atom '(' termlist ')'
    ;

atom
    : ATOM
    | STRING
    ;


predicateterm
    : simplepredicate
    | op='\\+' predicateterm
    | predicateterm op=',' predicateterm   // TODO make right assoc
    | predicateterm op='->' predicateterm
    | predicateterm op=';' predicateterm
    | '(' predicateterm ')'
    ;

termlist 
    : term
    | term ',' termlist
    ;

term 
    : NUMERAL
    | atom
    | functor
    | ATOM '/' NUMERAL
    | VARIABLE
    // | UNOP term
    | term BINOP term
    // | '(' term ')'
    | LBRACK RBRACK
    | LBRACK termlist RBRACK
    | LBRACK termlist '|' VARIABLE RBRACK
    ;

/*
query 
    : '?-' predicatelist '.'
    ;
*/

TRUE: 'true' ;
FAIL: 'fail' ;
CUT: '!' ;

VARIABLE 
    : UCLETTER CHARACTER*
    | '_'
    ;

ATOM 
    : LCLETTER CHARACTER*
    ;

NUMERAL 
    : DIGIT+
    ;

fragment CHARACTER 
    : LCLETTER | UCLETTER | DIGIT
    ;

/*
UNOP
    : '-' | '+'
    ;
*/

BINOP
    : '==' | '!=' | '<' | '>' | '<=' | '>='
    ;

/*
special 
    : '+' | '-' | '*' | '/' | '\\' | '^' | '~' | ':' | '.' | '?' | '#'| '$' | '&'
    ;
*/

STRING 
    : '\'' ( ~'\'' | '\\' '\'' )* '\''
    ;

LBRACK
    : '['
    ;

RBRACK
    : ']'
    ;

fragment LCLETTER
    : [a-z_];

fragment UCLETTER
    : [A-Z];

fragment DIGIT
    : [0-9];

WS
   : [ \t\r\n] -> skip
   ;

COMMENT
   : ( '%' .*? [\r\n] ) -> skip
   ;
