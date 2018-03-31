
exists(Person) :-
	husband(Person)
	;
	wife(Person)
	;
	child(Person).

child(X,P) :- mother(P,X) ; father(P,X).
daughter(X,P) :- (mother(P,X) ; father(P,X)) , female(X).
son(X,P) :- male(X) , ( mother(P,X) ; father(P,X) ).

samesexchild(X,P) :- male(X), father(P,X) ; female(X), mother(P,X) .

