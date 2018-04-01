
add(X,L,L) :- member(X,L), !.
add(X,L,cons(X,L)).


bubblesort(List,Sorted) :-
	swap(List,List1), !,
	bubblesort(List1,Sorted).

bubblesort(Sorted,Sorted).

