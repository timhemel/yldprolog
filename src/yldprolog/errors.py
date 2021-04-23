
class CompilerError(Exception):
    '''Error thrown during compilation.'''

    def __init__(self, filename, ctx, msg):
        '''filename is the filename in which the error occured, ctx is an ANTLR
        context, and msg is the error message.'''
        self.filename = filename
        self.line = ctx.start.line
        self.column = ctx.start.column
        self.message = msg

    def __str__(self):
        return f'{self.filename}:{self.line}:{self.column}:{self.message}'


