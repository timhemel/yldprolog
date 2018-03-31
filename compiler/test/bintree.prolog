
in(X,t(_,X,_)).
in(X1,t(L,_,_)) :- in(X1,L).
in(X2,t(_,_,R)) :- in(X2,R).

