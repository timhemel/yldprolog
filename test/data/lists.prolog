
empty([]).


member(X,[X|Tail]).
member(X,[Head|Tail]) :- member(X,Tail).

testlist([red,green,blue]).
