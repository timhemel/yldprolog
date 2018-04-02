

guilty(X) :- atcrimescene(X) -> noalibi(X) ; butler(X).

innocent(X) :- atcrimescene(X) -> alibi(X).

