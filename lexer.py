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
            'while': TokenType.KEYWORD_WHILE,
            'def': TokenType.KEYWORD_DEF,
            'return': TokenType.KEYWORD_RETURN,
            'True': TokenType.KEYWORD_TRUE,
            'False': TokenType.KEYWORD_FALSE,
            'None': TokenType.KEYWORD_NONE,
            'print': TokenType.KEYWORD_PRINT
        }

        self.full_regex = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        )

    def tokenize(self, code):
        tokens = []
        line_num = 1
        indent_stack = [0]

        # Tüm kodu satırlara ayır, her satırın sonunda '\n' karakterini koru
        # Bu, girinti analizi için önemlidir.
        lines = code.splitlines(keepends=True)

        # Son satır boş değilse ve '\n' ile bitmiyorsa, sona bir '\n' ekle
        # Bu, EOF öncesi son girinti kontrolünü sağlamak için önemlidir.
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'

        # Tüm kodun sonuna fazladan bir NEWLINE eklemek bazen parser'ın işini kolaylaştırır
        # (girinti kontrolü için). Ancak bu her zaman gerekli değildir.
        # Şimdilik mevcut mantığı koruyalım.

        for line_idx, line in enumerate(lines):
            original_line_num = line_num  # Geçerli satır numarasını koruyalım

            # Girinti miktarını belirle (sadece boşlukları say)
            current_line_indent = 0
            for char in line:
                if char == ' ':
                    current_line_indent += 1
                elif char == '\t':
                    current_line_indent += 4
                else:
                    break

            # Gerçek kod içeriğini al (girintileri atlayarak)
            code_content_on_line = line[current_line_indent:].rstrip('\n')  # Yeni satırı da atla

            # Yorum satırı mı veya sadece boşluk mu kontrol et
            is_empty_or_comment = False
            if not code_content_on_line.strip():  # Sadece boşluk veya boş satır
                is_empty_or_comment = True
            elif code_content_on_line.strip().startswith('#'):  # Yorum satırı
                is_empty_or_comment = True

            # Girinti kontrolü sadece boş olmayan, yorum olmayan satırlar için yapılmalı
            # VEYA, her satır için girinti token'ları üretip parser'ın boşlukları atlamasına izin verebiliriz.
            # Şu anki mantık, her satırın girintisini kontrol ediyor ve boş satırları atlıyor.
            # Boş satırlar için INDENT/DEDENT üretmemek önemlidir.

            if not is_empty_or_comment:
                if current_line_indent > indent_stack[-1]:
                    tokens.append(Token(TokenType.INDENT, '', original_line_num, indent_stack[-1]))
                    indent_stack.append(current_line_indent)
                elif current_line_indent < indent_stack[-1]:
                    while current_line_indent < indent_stack[-1]:
                        if not indent_stack:
                            raise RuntimeError(f"Aşırı girinti azaltma hatası (DEDENT) satır {original_line_num}")
                        tokens.append(Token(TokenType.DEDENT, '', original_line_num, indent_stack[-1]))
                        indent_stack.pop()
                    if current_line_indent != indent_stack[-1]:
                        raise RuntimeError(
                            f"Geçersiz girinti seviyesi satır {original_line_num}: {current_line_indent} yerine {indent_stack[-1]} bekleniyor")

            # Satır içi tokenleme
            current_column = 0
            while current_column < len(code_content_on_line):
                match = self.full_regex.match(code_content_on_line, current_column)

                if not match:
                    char = code_content_on_line[current_column]
                    tokens.append(
                        Token(TokenType.MISMATCH, char, original_line_num, current_line_indent + current_column))
                    print(
                        f"Uyarı: Tanımlanamayan karakter: '{char}' (Satır {original_line_num}, Sütun {current_line_indent + current_column})")
                    current_column += 1
                    continue

                kind = match.lastgroup
                value = match.group(kind)
                token_column = current_line_indent + match.start()

                if kind == 'WHITESPACE':
                    pass
                elif kind == 'NEWLINE':  # Bu durum normalde code_content_on_line'da olmaz, rstrip('\n') yüzünden
                    pass  # Burada NEWLINE token'ı üretmek yerine, satırın sonunda tek bir NEWLINE ekleyeceğiz.
                elif kind == 'IDENTIFIER' and value in self.keywords:
                    tokens.append(Token(self.keywords[value], value, original_line_num, token_column))
                elif kind == 'STRING':
                    tokens.append(Token(TokenType.STRING, value, original_line_num, token_column))
                elif kind == 'OPERATOR':
                    tokens.append(Token(TokenType.OPERATOR, value, original_line_num, token_column))
                elif kind in ['LPAREN', 'RPAREN', 'COLON', 'COMMA']:
                    tokens.append(Token(TokenType[kind], value, original_line_num, token_column))
                elif kind == 'COMMENT':  # Yorum token'ı olarak ekle
                    tokens.append(Token(TokenType.COMMENT, value, original_line_num, token_column))
                else:
                    tokens.append(Token(TokenType[kind], value, original_line_num, token_column))

                current_column = match.end()

            # Her satırın sonunda bir NEWLINE token'ı ekle, sadece boş veya yorum satırı değilse
            # VEYA, her satırın sonunda ekle, parser'ın yorumları atlamasına izin ver.
            # Python'da yorum satırları da bir NEWLINE ile biter ve lexer yorumu token'laştırdıktan sonra
            # satır sonu da bir NEWLINE token'ı olarak üretilmelidir.
            tokens.append(Token(TokenType.NEWLINE, '\n', original_line_num, len(line.rstrip('\n'))))

            line_num += 1  # Bir sonraki satıra geç

        # Dosyanın sonunda kalan tüm açık girintileri kapat
        while indent_stack[-1] > 0:
            tokens.append(Token(TokenType.DEDENT, '', line_num - 1, 0))  # Son satırda DEDENT
            indent_stack.pop()

        tokens.append(Token(TokenType.EOF, '', line_num - 1, 0))  # EOF'un doğru satırda olduğundan emin olalım
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
