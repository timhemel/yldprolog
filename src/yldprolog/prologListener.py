# Generated from prolog.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .prologParser import prologParser
else:
    from prologParser import prologParser

# This class defines a complete listener for a parse tree produced by prologParser.
class prologListener(ParseTreeListener):

    # Enter a parse tree produced by prologParser#program.
    def enterProgram(self, ctx:prologParser.ProgramContext):
        pass

    # Exit a parse tree produced by prologParser#program.
    def exitProgram(self, ctx:prologParser.ProgramContext):
        pass


    # Enter a parse tree produced by prologParser#clauseordirective.
    def enterClauseordirective(self, ctx:prologParser.ClauseordirectiveContext):
        pass

    # Exit a parse tree produced by prologParser#clauseordirective.
    def exitClauseordirective(self, ctx:prologParser.ClauseordirectiveContext):
        pass


    # Enter a parse tree produced by prologParser#clause.
    def enterClause(self, ctx:prologParser.ClauseContext):
        pass

    # Exit a parse tree produced by prologParser#clause.
    def exitClause(self, ctx:prologParser.ClauseContext):
        pass


    # Enter a parse tree produced by prologParser#directive.
    def enterDirective(self, ctx:prologParser.DirectiveContext):
        pass

    # Exit a parse tree produced by prologParser#directive.
    def exitDirective(self, ctx:prologParser.DirectiveContext):
        pass


    # Enter a parse tree produced by prologParser#predicatelist.
    def enterPredicatelist(self, ctx:prologParser.PredicatelistContext):
        pass

    # Exit a parse tree produced by prologParser#predicatelist.
    def exitPredicatelist(self, ctx:prologParser.PredicatelistContext):
        pass


    # Enter a parse tree produced by prologParser#predicateexpression.
    def enterPredicateexpression(self, ctx:prologParser.PredicateexpressionContext):
        pass

    # Exit a parse tree produced by prologParser#predicateexpression.
    def exitPredicateexpression(self, ctx:prologParser.PredicateexpressionContext):
        pass


    # Enter a parse tree produced by prologParser#simplepredicate.
    def enterSimplepredicate(self, ctx:prologParser.SimplepredicateContext):
        pass

    # Exit a parse tree produced by prologParser#simplepredicate.
    def exitSimplepredicate(self, ctx:prologParser.SimplepredicateContext):
        pass


    # Enter a parse tree produced by prologParser#termpredicate.
    def enterTermpredicate(self, ctx:prologParser.TermpredicateContext):
        pass

    # Exit a parse tree produced by prologParser#termpredicate.
    def exitTermpredicate(self, ctx:prologParser.TermpredicateContext):
        pass


    # Enter a parse tree produced by prologParser#termlist.
    def enterTermlist(self, ctx:prologParser.TermlistContext):
        pass

    # Exit a parse tree produced by prologParser#termlist.
    def exitTermlist(self, ctx:prologParser.TermlistContext):
        pass


    # Enter a parse tree produced by prologParser#term.
    def enterTerm(self, ctx:prologParser.TermContext):
        pass

    # Exit a parse tree produced by prologParser#term.
    def exitTerm(self, ctx:prologParser.TermContext):
        pass


    # Enter a parse tree produced by prologParser#atom.
    def enterAtom(self, ctx:prologParser.AtomContext):
        pass

    # Exit a parse tree produced by prologParser#atom.
    def exitAtom(self, ctx:prologParser.AtomContext):
        pass


    # Enter a parse tree produced by prologParser#functor.
    def enterFunctor(self, ctx:prologParser.FunctorContext):
        pass

    # Exit a parse tree produced by prologParser#functor.
    def exitFunctor(self, ctx:prologParser.FunctorContext):
        pass



del prologParser