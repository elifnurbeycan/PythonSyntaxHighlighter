# parser.py
from tokens import TokenType, Token
from syntax_tree import *


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while self.peek().type != TokenType.EOF:
            # Başlangıçta ve her statement'tan önce boş satırları atla
            while self.match(TokenType.NEWLINE):
                pass

            # Yorumları da burada atlayabiliriz, Lexer'da COMMENT olarak token'laştığı varsayımıyla
            while self.match(TokenType.COMMENT):
                self.match(TokenType.NEWLINE)  # Yorumdan sonra NEWLINE varsa tüket
                pass

            if self.peek().type == TokenType.EOF:  # Yorum ve boş satırlardan sonra EOF geldiyse
                break

            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)

                # Her statement'tan sonra NEWLINE bekliyoruz (Python'ın kuralı)
                # Ancak EOF gelmediyse ve NEWLINE yoksa hata fırlatabiliriz.
                if self.peek().type != TokenType.EOF and not self.check(TokenType.NEWLINE):
                    # print(f"Uyarı: Statement sonrası NEWLINE bekleniyor, bulundu: {self.peek()}")
                    pass  # Şimdilik uyarı verelim, katı bir kural koymayalım

                # Son statement'tan sonra veya bir bloktan sonra kalan NEWLINE'ları tüket
                while self.match(TokenType.NEWLINE):
                    pass

            except ParserError as e:
                print(f"Parser Hatası: {e} - Hata Token: {self.peek()}")
                # Hata durumunda parser'ı ilerletmeye çalış
                # Bir sonraki NEWLINE'a veya EOF'a kadar atla
                while self.peek().type not in [TokenType.NEWLINE, TokenType.EOF]:
                    self.advance()
                if self.peek().type == TokenType.NEWLINE:
                    self.advance()  # Yeni satırı atla
                else:
                    break  # EOF'a ulaşıldıysa döngüyü bitir
        return ProgramNode(statements)

    def parse_statement(self):
        token = self.peek()

        if token.type == TokenType.COMMENT:  # Yorumu atla, AST'ye ekleme
            self.advance()
            # Yorumdan sonra NEWLINE olması beklenir. Eğer yoksa, lexer'ın hatasıdır.
            # self.consume(TokenType.NEWLINE, None) # Yorumdan sonra NEWLINE bekleriz, yoksa hata
            return None  # Yorumlar AST'ye girmez

        if self.check_keyword(TokenType.KEYWORD_IF):
            return self.parse_if_statement()
        elif self.check_keyword(TokenType.KEYWORD_WHILE):
            return self.parse_while_statement()
        elif self.check_keyword(TokenType.KEYWORD_DEF):
            return self.parse_function_def()
        elif self.check_keyword(TokenType.KEYWORD_RETURN):
            return self.parse_return_statement()

        # Atama veya Expression Statement
        expr = self.parse_expression()

        # Atama operatörü sadece eşittir (=)
        if self.match(TokenType.OPERATOR) and self.previous().value == '=':
            if not isinstance(expr, VariableNode):
                raise ParserError(f"Geçersiz atama hedefi: {expr} (Satır {token.line})")
            return AssignmentNode(expr.name, self.parse_expression())

        return ExpressionStatementNode(expr)

    def parse_expression(self):
        # Basitlik adına, sadece karşılaştırma ve aritmetik işlemleri destekleyelim
        return self.parse_comparison()

    def parse_comparison(self):
        expr = self.parse_term()
        # Operatörler listesi (string değerleriyle)
        ops = ['==', '!=', '<', '>', '<=', '>=']
        while self.check(TokenType.OPERATOR) and self.peek().value in ops:
            operator_token = self.advance()
            right = self.parse_term()
            expr = BinaryOpNode(expr, operator_token.value, right)
        return expr

    def parse_term(self):  # Toplama/Çıkarma
        expr = self.parse_factor()
        ops = ['+', '-']
        while self.check(TokenType.OPERATOR) and self.peek().value in ops:
            operator_token = self.advance()
            right = self.parse_factor()
            expr = BinaryOpNode(expr, operator_token.value, right)
        return expr

    def parse_factor(self):  # Çarpma/Bölme/Modül
        expr = self.parse_unary()
        ops = ['*', '/', '%']
        while self.check(TokenType.OPERATOR) and self.peek().value in ops:
            operator_token = self.advance()
            right = self.parse_unary()
            expr = BinaryOpNode(expr, operator_token.value, right)
        return expr

    def parse_unary(self):
        if self.match(TokenType.OPERATOR) and self.previous().value == '-':
            operator = self.previous().value
            operand = self.parse_unary()
            return UnaryOpNode(operator, operand)
        return self.parse_primary()

    def parse_primary(self):
        if self.match(TokenType.NUMBER):
            return NumberNode(float(self.previous().value))
        if self.match(TokenType.STRING):
            return StringNode(self.previous().value[1:-1])  # Tırnakları kaldır
        if self.match_keyword(TokenType.KEYWORD_TRUE):
            return BooleanNode(True)
        if self.match_keyword(TokenType.KEYWORD_FALSE):
            return BooleanNode(False)
        if self.match_keyword(TokenType.KEYWORD_NONE):
            return NoneNode()

        if self.check(TokenType.IDENTIFIER):
            name_token = self.advance()
            # print fonksiyonu için özel kontrol
            if name_token.type == TokenType.KEYWORD_PRINT or (
                    name_token.type == TokenType.IDENTIFIER and name_token.value == 'print'):
                # Python'da print bir fonksiyon çağrısıdır: print(arg)
                self.consume(TokenType.LPAREN, '(')
                args = self.parse_arguments()
                self.consume(TokenType.RPAREN, ')')
                return CallNode("print", args)  # Fonksiyon adı string olarak

            # Diğer fonksiyon çağrıları (kullanıcı tanımlı)
            if self.match(TokenType.LPAREN):
                args = self.parse_arguments()
                self.consume(TokenType.RPAREN, ')')
                return CallNode(name_token.value, args)

            return VariableNode(name_token.value)

        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, ')')
            return expr

        raise ParserError(f"Beklenen ifade bulunamadı, ancak bulundu: {self.peek()}")

    def parse_arguments(self):
        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expression())
        return args

    # --- Blok ve Yapısal Metodlar ---
    def parse_block(self):
        statements = []
        # Blok başlamadan önce beklenen NEWLINE token'larını tüket
        while self.match(TokenType.NEWLINE):
            pass

        self.consume(TokenType.INDENT, None)  # Beklenen INDENT token'ını tüket

        while not (self.check(TokenType.DEDENT) or self.peek().type == TokenType.EOF):
            # Blok içindeki her statement'tan önce NEWLINE ve COMMENT'ları atla
            while self.match(TokenType.NEWLINE) or self.match(TokenType.COMMENT):
                if self.previous().type == TokenType.COMMENT:
                    self.match(TokenType.NEWLINE)  # Yorumdan sonra NEWLINE varsa tüket
                pass

            # Eğer hala DEDENT gelmediyse ve EOF değilse, bir ifade ayrıştır
            if not (self.check(TokenType.DEDENT) or self.peek().type == TokenType.EOF):
                stmt = self.parse_statement()
                if stmt:  # Yorumlar None döndürdüğü için sadece geçerli statement'ları ekle
                    statements.append(stmt)

                # Her statement sonrası NEWLINE bekliyoruz, yoksa hata
                # (Şimdilik esnek olalım, eğer NEWLINE yoksa da devam etsin ama hata fırlatabiliriz)
                if self.peek().type != TokenType.EOF and not self.check(TokenType.NEWLINE) and not self.check(
                        TokenType.DEDENT):
                    # print(f"Uyarı: Blok içinde statement sonrası NEWLINE bekleniyor, bulundu: {self.peek()}")
                    pass

                while self.match(TokenType.NEWLINE):  # Statement sonrası kalan NEWLINE'ları atla
                    pass

        # Blok bittiğinde DEDENT token'ını tüket
        self.consume(TokenType.DEDENT, None)
        return statements

    def parse_if_statement(self):
        self.consume_keyword(TokenType.KEYWORD_IF)
        condition = self.parse_expression()
        self.consume(TokenType.COLON, ':')
        self.consume(TokenType.NEWLINE)  # Koşuldan sonraki NEWLINE'ı tüket

        body = self.parse_block()  # INDENT/DEDENT tarafından yönetilen blok

        else_body = []
        if self.check_keyword(TokenType.KEYWORD_ELSE):
            # Else'den önce DEDENT zaten parse_block tarafından tüketilmelidir
            # Eğer parser'ın DEDENT'ı tüketmediği bir durum varsa burada bir hata olabilir.

            self.advance()  # ELSE keyword'ünü tüket
            self.consume(TokenType.COLON, ':')
            self.consume(TokenType.NEWLINE)  # ELSE'den sonraki NEWLINE'ı tüket
            else_body = self.parse_block()

        return IfNode(condition, body, else_body)

    def parse_while_statement(self):
        self.consume_keyword(TokenType.KEYWORD_WHILE)
        condition = self.parse_expression()
        self.consume(TokenType.COLON, ':')
        self.consume(TokenType.NEWLINE)
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_function_def(self):
        self.consume_keyword(TokenType.KEYWORD_DEF)
        name = self.consume(TokenType.IDENTIFIER, None)
        self.consume(TokenType.LPAREN, '(')
        params = self.parse_parameters()
        self.consume(TokenType.RPAREN, ')')
        self.consume(TokenType.COLON, ':')
        self.consume(TokenType.NEWLINE)
        body = self.parse_block()
        return FunctionDefNode(name.value, params, body)

    def parse_parameters(self):
        params = []
        if not self.check(TokenType.RPAREN):
            params.append(self.consume(TokenType.IDENTIFIER, None).value)
            while self.match(TokenType.COMMA):
                params.append(self.consume(TokenType.IDENTIFIER, None).value)
        return params

    def parse_return_statement(self):
        self.consume_keyword(TokenType.KEYWORD_RETURN)
        # Return ifadesi opsiyoneldir, ancak hemen NEWLINE gelirse ifade yoktur
        if not (self.check(TokenType.NEWLINE) or self.peek().type == TokenType.EOF):
            expr = self.parse_expression()
            return ReturnNode(expr)
        return ReturnNode(None)

    # --- Yardımcı Fonksiyonlar ---
    def match(self, type_, value_to_check=None):
        if self.check(type_, value_to_check):
            self.advance()
            return True
        return False

    def match_keyword(self, keyword_type):
        if self.check_keyword(keyword_type):
            self.advance()
            return True
        return False

    def consume(self, type_, value_to_check=None):
        if self.check(type_, value_to_check):
            return self.advance()
        actual = self.peek()
        expected_str = type_.name
        if value_to_check:
            expected_str += f" ('{value_to_check}')"
        # Hata mesajında token'ın tam değerini ve konumunu ekle
        raise ParserError(
            f"Beklenen {expected_str} ancak bulundu: {actual.type.name} ('{actual.value}') (Satır {actual.line}, Sütun {actual.column})")

    def consume_keyword(self, keyword_type):
        if self.check_keyword(keyword_type):
            return self.advance()
        actual = self.peek()
        raise ParserError(
            f"Beklenen anahtar kelime {keyword_type.name} ancak bulundu: {actual.type.name} ('{actual.value}') (Satır {actual.line}, Sütun {actual.column})")

    def check(self, type_, value_to_check=None):
        if self.is_at_end():
            return False
        token = self.peek()
        if token.type != type_:
            return False
        if value_to_check is not None and token.value != value_to_check:
            return False
        return True

    def check_keyword(self, keyword_type):
        if self.is_at_end():
            return False
        token = self.peek()
        return token.type == keyword_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self):
        return self.tokens[self.current - 1]

    def peek(self):
        if self.current >= len(self.tokens):
            # EOF token'ının doğru satır ve sütun bilgisini vermeye çalış
            # Eğer token listesi boşsa, varsayılan bir konum ver.
            last_token_line = self.tokens[-1].line if self.tokens else 1
            last_token_col = self.tokens[-1].column + len(self.tokens[-1].value) if self.tokens else 0
            return Token(TokenType.EOF, '', line=last_token_line, column=last_token_col)
        return self.tokens[self.current]

    def is_at_end(self):
        # Sadece EOF token'ına ulaşıldığında son olarak kabul et
        return self.peek().type == TokenType.EOF