
add(X,L,L) :- member(X,L).

foo(X,L,bar(L,A)) :- member(X,L), member(A,L).
