
likes(A,B) :- person(A), person(B), friend(A,B).

likes(A,B,C) :- person(A),person(B), person(C), friend(A,B), friend(A,C).

