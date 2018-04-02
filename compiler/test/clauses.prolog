parent(tom,liz).

offspring(Y,X) :- parent(X,Y).

grandparent(X,Z) :- parent(X,Y), parent(Y,Z).

