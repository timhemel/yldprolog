
in(X,t(_,X,_)).
in(X,t(L,_,_)) :- in(X,L).
in(X,t(_,_,R)) :- in(X,R).

