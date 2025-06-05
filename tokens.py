# tokens.py
from enum import Enum

class TokenType(Enum):
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    OPERATOR = 'OPERATOR'
    KEYWORD = 'KEYWORD'
    NEWLINE = 'NEWLINE'
    COMMENT = 'COMMENT'
    EOF = 'EOF'
    MISMATCH = 'MISMATCH'
    # Yeni eklenenler:
    INDENT = 'INDENT'
    DEDENT = 'DEDENT'

class Token:
    def __init__(self, type_, value, line=0, column=0):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.column})"