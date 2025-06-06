# tokens.py
from enum import Enum

class TokenType(Enum):
    # Anahtar Kelimeler
    KEYWORD_IF = 'IF'
    KEYWORD_ELSE = 'ELSE'
    KEYWORD_ELIF = 'ELIF'
    KEYWORD_WHILE = 'WHILE'
    KEYWORD_DEF = 'DEF'
    KEYWORD_RETURN = 'RETURN'
    KEYWORD_TRUE = 'TRUE'
    KEYWORD_FALSE = 'FALSE'
    KEYWORD_NONE = 'NONE'
    KEYWORD_PRINT = 'PRINT' # 'print' için özel bir anahtar kelime

    # Operatörler
    OPERATOR = 'OPERATOR' # Tüm operatörler için tek tip
    EQ = '=='
    NE = '!='
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    MODULO = '%'

    # Mantıksal Operatörler <-- YENİ EKLENDİ
    KEYWORD_AND = 'AND'
    KEYWORD_OR = 'OR'
    KEYWORD_NOT = 'NOT'

    # Ayraclar / Ayraçlar
    LPAREN = '('
    RPAREN = ')'
    COLON = ':'
    COMMA = ','

    # Literaller
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    BOOLEAN = 'BOOLEAN' # True/False için genel bir boolean tipi (isteğe bağlı, KEYWORD_TRUE/FALSE zaten var)

    # Özel Token Tipleri
    COMMENT = 'COMMENT'
    WHITESPACE = 'WHITESPACE'
    NEWLINE = 'NEWLINE'
    INDENT = 'INDENT'
    DEDENT = 'DEDENT'
    EOF = 'EOF' # End Of File
    MISMATCH = 'MISMATCH' # Tanımlanamayan karakterler için

class Token:
    def __init__(self, type, value, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        # Sütun bilgisi de eklenerek daha detaylı bir temsil
        return f"Token(Type:{self.type.name}, Value:'{self.value}', Line:{self.line}, Col:{self.column})"
