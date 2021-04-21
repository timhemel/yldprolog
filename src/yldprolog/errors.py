
class ParseError(Exception):
    def __init__(self, filename, ctx, msg):
        self.filename = filename
        self.line = ctx.start.line
        self.column = ctx.start.column
        self.message = msg

    def __str__(self):
        return f'{self.filename}:{self.line}:{self.column}:{self.message}'


