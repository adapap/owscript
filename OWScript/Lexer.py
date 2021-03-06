import functools
import re

from . import Errors
from .Tokens import Token, Tokens

class Lexer:
    IGNORE = ('WHITESPACE', 'SEMI', 'COMMENT', 'ANNOTATION')
    NEWLINE = functools.partial(Token, type='NEWLINE', value='\n')
    INDENT = functools.partial(Token, type='INDENT', value='⮡')
    DEDENT = functools.partial(Token, type='DEDENT', value='⮢')
    EOF = functools.partial(Token, type='EOF', value='')
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indents = []
        self.tokens = []

    def print_tokens(self):
        """Outputs the current token list."""
        tokens = '\n'.join(map(repr, self.tokens))
        print(tokens)
        return tokens

    def lex(self):
        """Tokenizes input into a list of tokens."""
        expressions = [(token, re.compile(pattern, re.I)) for token, pattern in Tokens.__annotations__.items()]
        whitespace_pattern = re.compile(Tokens.__annotations__.get('WHITESPACE'))
        self.indents.append(0)
        while self.pos < len(self.text):
            for token_type, pattern in expressions:
                match = pattern.match(self.text, self.pos)
                if match:
                    value = match.group(1) if token_type == 'OWID' else match.group(0)
                    token = Token(type=token_type, value=value, line=self.line, column=self.column)
                    if value:
                        self.pos += len(value)
                    if token.type == 'NEWLINE':
                        token.value = r'\n'
                        self.tokens.append(token)
                        self.line += match.group(0).count('\n')
                        match = whitespace_pattern.match(self.text, self.pos)
                        self.column = len(match.group(0).replace('\t', ' ' * 4)) + 1 if match else 1
                        spaces = self.column - 1
                        if spaces > self.indents[-1]:
                            indent = Lexer.INDENT(line=self.line, column=self.column)
                            self.tokens.append(indent)
                            self.indents.append(spaces)
                        elif spaces < self.indents[-1]:
                            while spaces < self.indents[-1]:
                                self.indents.pop()
                                self.column = spaces + 1
                                dedent = Lexer.DEDENT(line=self.line, column=self.column)
                                self.tokens.append(dedent)
                        else:
                            self.column = spaces + 1
                        if match:
                            self.pos = match.end()
                        break
                    elif token.type in Lexer.IGNORE:
                        self.column += len(token.value)
                        self.line += token.value.count('\n')
                        break
                    else:
                        self.tokens.append(token)
                    self.column += len(token.value)
                    break
            else:
                Errors.POS = (self.line, self.column)
                raise Errors.LexError("Unexpected symbol '{}'".format(self.text[self.pos]))
        while self.indents[-1] > 0:
            self.column = self.indents.pop()
            dedent = Lexer.DEDENT(line=self.line, column=self.column)
            self.tokens.append(dedent)
        self.tokens.append(Lexer.EOF(line=self.line, column=0))
        return self.tokens