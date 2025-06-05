# tokens.py
from enum import Enum


class TokenType(Enum):
    # Temel Tipler
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'

    # Operatörler (daha az detaylı, genel OPERATOR altında toplayabiliriz)
    OPERATOR = 'OPERATOR'  # Genel operatörler için

    # Noktalama İşaretleri
    LPAREN = 'LPAREN'  # (
    RPAREN = 'RPAREN'  # )
    COLON = 'COLON'  # :
    COMMA = 'COMMA'  # ,

    # Anahtar Kelimeler (Sadece temel Python anahtar kelimeleri)
    KEYWORD_IF = 'IF'
    KEYWORD_ELSE = 'ELSE'
    # KEYWORD_ELIF kaldırıldı
    KEYWORD_WHILE = 'WHILE'
    # KEYWORD_FOR kaldırıldı
    KEYWORD_DEF = 'DEF'
    KEYWORD_RETURN = 'RETURN'
    KEYWORD_TRUE = 'TRUE'
    KEYWORD_FALSE = 'FALSE'
    KEYWORD_NONE = 'NONE'
    # KEYWORD_AND, KEYWORD_OR, KEYWORD_NOT, KEYWORD_IN kaldırıldı
    KEYWORD_PRINT = 'PRINT'  # Print fonksiyonu için keyword olarak bırakalım

    # Yapısal Tokenler
    NEWLINE = 'NEWLINE'
    INDENT = 'INDENT'
    DEDENT = 'DEDENT'
    COMMENT = 'COMMENT'
    EOF = 'EOF'
    MISMATCH = 'MISMATCH'  # Tanımlanamayan karakterler için


class Token:
    def __init__(self, type_, value, line=0, column=0):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.column})"
