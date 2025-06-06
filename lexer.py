# lexer.py
import re
from tokens import Token, TokenType


class Lexer:
    def __init__(self):
        self.token_specs = [
            # Operatörler: Önce uzun olanlar gelmeli (örneğin '==' önce '=' den)
            ('OPERATOR', r'==|!=|<=|>=|<|>|=|\+|-|\*|/|%'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('COLON', r':'),
            ('COMMA', r','),

            ('STRING', r'(\"[^\"]*\"|\'[^\']*\')'),  # Tırnak içinde her şeyi yakala
            ('COMMENT', r'#.*'),
            ('NUMBER', r'\b\d+(\.\d*)?|\.\d+\b'),  # 123, 123.45, .5 gibi
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Anahtar kelimelerden sonra gelmeli

            ('WHITESPACE', r'[ \t]+'),  # Boşlukları atla, NEWLINE'lar ayrılacak
            ('NEWLINE', r'\n'),  # Yeni satır karakteri
            ('MISMATCH', r'.'),  # Kalan her şey
        ]

        self.keywords = {
            'if': TokenType.KEYWORD_IF,
            'else': TokenType.KEYWORD_ELSE,
            'elif': TokenType.KEYWORD_ELIF,
            'while': TokenType.KEYWORD_WHILE,
            'def': TokenType.KEYWORD_DEF,
            'return': TokenType.KEYWORD_RETURN,
            'True': TokenType.KEYWORD_TRUE,
            'False': TokenType.KEYWORD_FALSE,
            'None': TokenType.KEYWORD_NONE,
            'print': TokenType.KEYWORD_PRINT,
            'and': TokenType.KEYWORD_AND,
            'or': TokenType.KEYWORD_OR,
            'not': TokenType.KEYWORD_NOT
        }

        self.full_regex = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        )

    def tokenize(self, code):
        tokens = []
        line_num = 1
        indent_stack = [0]

        lines = code.splitlines(keepends=True)
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'

        for line_idx, line in enumerate(lines):
            # Boş satırları tamamen atla. Lexer boş satırlar için token üretmemeli.
            if not line.strip():
                line_num += 1
                continue

            current_line_indent = 0
            for char in line:
                if char == ' ':
                    current_line_indent += 1
                elif char == '\t':
                    current_line_indent += 4
                else:
                    break

            code_content_on_line = line[current_line_indent:].rstrip('\n')

            # Yorum satırları için sadece COMMENT token'ı ve NEWLINE üret
            if code_content_on_line.startswith('#'):
                tokens.append(Token(TokenType.COMMENT, code_content_on_line, line_num, current_line_indent))
                tokens.append(Token(TokenType.NEWLINE, '\n', line_num, len(line.rstrip('\n'))))
                line_num += 1
                continue

            # Girinti kontrolü (sadece boş ve yorum olmayan satırlar için)
            if current_line_indent > indent_stack[-1]:
                tokens.append(Token(TokenType.INDENT, '', line_num, indent_stack[-1]))
                indent_stack.append(current_line_indent)
            elif current_line_indent < indent_stack[-1]:
                while current_line_indent < indent_stack[-1]:
                    if not indent_stack:
                        raise RuntimeError(f"Aşırı girinti azaltma hatası (DEDENT) satır {line_num}")
                    tokens.append(Token(TokenType.DEDENT, '', line_num, indent_stack[-1]))
                    indent_stack.pop()
                if current_line_indent != indent_stack[-1]:
                    raise RuntimeError(
                        f"Geçersiz girinti seviyesi satır {line_num}: {current_line_indent} yerine {indent_stack[-1]} bekleniyor")

            # Satır içi tokenleme (gerçek kod içeriği için)
            current_column = 0
            while current_column < len(code_content_on_line):
                match = self.full_regex.match(code_content_on_line, current_column)

                if not match:
                    char = code_content_on_line[current_column]
                    tokens.append(Token(TokenType.MISMATCH, char, line_num, current_line_indent + current_column))
                    print(
                        f"Uyarı: Tanımlanamayan karakter: '{char}' (Satır {line_num}, Sütun {current_line_indent + current_column})")
                    current_column += 1
                    continue

                kind = match.lastgroup
                value = match.group(kind)
                token_column = current_line_indent + match.start()

                if kind == 'WHITESPACE':
                    pass
                elif kind == 'IDENTIFIER' and value in self.keywords:
                    tokens.append(Token(self.keywords[value], value, line_num, token_column))
                elif kind == 'STRING':
                    tokens.append(Token(TokenType.STRING, value, line_num, token_column))
                elif kind == 'OPERATOR':
                    tokens.append(Token(TokenType.OPERATOR, value, line_num, token_column))
                elif kind in ['LPAREN', 'RPAREN', 'COLON', 'COMMA']:
                    tokens.append(Token(TokenType[kind], value, line_num, token_column))
                else:
                    tokens.append(Token(TokenType[kind], value, line_num, token_column))

                current_column = match.end()

            # Her kod satırının sonunda bir NEWLINE token'ı ekle
            tokens.append(Token(TokenType.NEWLINE, '\n', line_num, len(line.rstrip('\n'))))
            line_num += 1

        # Dosyanın sonunda kalan tüm açık girintileri kapat
        while indent_stack[-1] > 0:
            tokens.append(Token(TokenType.DEDENT, '', line_num - 1, 0))
            indent_stack.pop()

        # En sona EOF token'ı ekle
        tokens.append(Token(TokenType.EOF, '', line_num - 1, 0))
        return tokens


# Lexer test bloğu (basitleştirilmiş)
if __name__ == '__main__':
    test_code = """
x = 10
if x == 5:
    print("Merhaba.")
else:
    print("Farklı.")
def f(a, b):
    return a + b
# Yorum
"""
    lexer = Lexer()
    print("\n--- Lexer Test (Basit Python Syntax) ---")
    try:
        test_tokens = lexer.tokenize(test_code)
        for t in test_tokens:
            print(t)
    except RuntimeError as e:
        print(f"Lexer Hatası: {e}")
