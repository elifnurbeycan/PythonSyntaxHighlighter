# lexer.py (sadece ilgili kısımları güncelleyin)
import re
from tokens import Token, TokenType  # TokenType'ı import ettiğimize emin olun


class Lexer:
    def __init__(self):
        self.token_specs = [
            # INDENT/DEDENT regexleri burada kullanılmıyor,
            # lexer'ın tokenize metodu içinde manuel olarak işleniyorlar.
            # Bu regexleri burada bırakmak hata değil ama kullanılmadığını unutmayın.
            ('KEYWORD',
             r'\b(if|else|while|for|def|return|True|False|None|continue|break|print|then|endif|endwhile|and|or)\b'),
            ('OPERATOR', r'==|!=|<=|>=|<|>|=|!|\+|-|\*|/|%|\(|\)|\[|\]|\{|\}|:|,|\.'),
            ('STRING', r'(\".*?\"|\'.*?\')'),
            ('NUMBER', r'\b\d+(\.\d*)?|\.\d+\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('COMMENT', r'#.*'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),  # Boşlukları atlamak için
            ('MISMATCH', r'.'),  # Her zaman en sonda olmalı
        ]
        self.token_regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs))

    def tokenize(self, code):
        tokens = []
        line_num = 1
        line_start = 0
        indent_stack = [0]  # Girinti seviyelerini takip eden stack

        # Satır sonlarındaki boşlukları korumak için splitlines(keepends=True)
        lines = code.splitlines(keepends=True)

        for line_idx, line in enumerate(lines):  # line_idx ekledik
            # Satır sonundaki boş satırları ve sadece boşluk içeren satırları kontrol et
            if not line.strip() and line_idx == len(lines) - 1 and not line.endswith('\n'):
                # Sadece son satır boşsa veya boşluktan ibaretse ve yeni satır içermiyorsa atla
                break

            current_line_indent = len(line) - len(line.lstrip(' '))  # Sadece boşlukları say
            line_content = line.lstrip(' ')  # Sadece boşlukları atla

            # Girinti değişim kontrolü
            if current_line_indent > indent_stack[-1]:
                # Yeni girinti bloğu başladı
                tokens.append(
                    Token(TokenType.INDENT, ' ' * (current_line_indent - indent_stack[-1]), line_num, indent_stack[-1]))
                indent_stack.append(current_line_indent)
            elif current_line_indent < indent_stack[-1]:
                # Girinti azaldı, DEDENT üret
                while current_line_indent < indent_stack[-1]:
                    tokens.append(Token(TokenType.DEDENT, '', line_num,
                                        indent_stack[-1]))  # DEDENT'in kolonu başlangıç indent'i olabilir
                    indent_stack.pop()
                    if not indent_stack:  # Stack boşalırsa (çok fazla dedent)
                        raise RuntimeError(f"Aşırı girinti azaltma hatası (DEDENT) satır {line_num}")
                # Eğer girinti seviyesi eşleşmezse (geçersiz girinti)
                if current_line_indent != indent_stack[-1]:
                    raise RuntimeError(
                        f"Geçersiz girinti seviyesi satır {line_num}: {current_line_indent} yerine {indent_stack[-1]} bekleniyor")

            # Satır içi tokenleme (girinti sonrası içerik)
            col_offset = current_line_indent  # Token'ın gerçek sütununu hesaplamak için
            temp_line_pos = 0  # current_line_indent sonrası pozisyon

            for mo in self.token_regex.finditer(line_content):
                kind = mo.lastgroup
                value = mo.group()

                # Token'ın gerçek sütununu hesapla
                # Bu, satırın başından (yani ilk boşluklardan sonra) itibaren olan mo.start() + boşluklar
                column = mo.start() + col_offset

                if kind == 'NEWLINE':
                    # NEWLINE tokenları zaten splitlines(keepends=True) ile işlendi
                    # Eğer son karakter \n ise ve onu bir token olarak ekliyorsak,
                    # bu kısım gereksiz olabilir veya farklı işlenebilir.
                    # Eğer splitlines() kullandığımız için '\n' zaten ayıklanmışsa,
                    # NEWLINE regex kuralını kaldırmamız gerekebilir.
                    # Ancak şu anki yapıda, line_content içinde '\n' varsa eşleşir.
                    tokens.append(Token(TokenType.NEWLINE, value, line_num, column))
                elif kind == 'SKIP':
                    continue  # Boşlukları atla
                elif kind == 'MISMATCH':
                    # Hata fırlatmak yerine bir MISMATCH token'ı ekleyelim
                    tokens.append(Token(TokenType.MISMATCH, value, line_num, column))
                    print(f'Uyarı: Tanımlanamayan karakter: {value!r} (Satır {line_num}, Sütun {column})')
                else:
                    tokens.append(Token(TokenType[kind], value, line_num, column))

            line_num += 1
            # line_start'ı güncellemeyi dikkatli yapmalıyız, her satır için baştan alıyoruz
            # line_start += len(line) # Bu, önceki global line_start mantığıydı, artık her satırı bağımsız işliyoruz.
            # Sadece bir sonraki satıra geçmek için line_num'ı artırıyoruz.

        # DOSYA SONUNDA KALAN GİRİNTİLERİ KAPAT (EOF'tan önce)
        while indent_stack[-1] > 0:
            tokens.append(Token(TokenType.DEDENT, '', line_num, 0))  # Sütun 0 uygun olabilir
            indent_stack.pop()

        tokens.append(Token(TokenType.EOF, '', line_num, 0))  # EOF her zaman en sona eklenir
        return tokens


# Test kısmı
if __name__ == '__main__':
    test_code = """
x = 10
if x > 5 then
  print "Greater"
else
  print "Smaller"
endif
    """  # Başlangıçta ekstra boşluk olmamasına dikkat edin

    # Lexer'ı test etmek için basit bir örnek
    lexer = Lexer()
    print("\n--- Lexer Test ---")
    try:
        test_tokens = lexer.tokenize(test_code)
        for t in test_tokens:
            print(t)
    except RuntimeError as e:
        print(f"Lexer Hatası: {e}")
