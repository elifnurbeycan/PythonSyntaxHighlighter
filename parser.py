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
            self.skip_whitespace_and_comments()

            if self.peek().type == TokenType.EOF:
                break

            # Hata toparlama için bir checkpoint oluştur
            start_index = self.current
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
                self.skip_newlines()  # Her statement'tan sonra NEWLINE'ları atla
            except ParserError as e:
                # Hata durumunda parser'ın akışını iyileştirmek için
                # Geçerli token'ı logla ve bir sonraki güvenli noktaya atla.
                print(f"Parser Hatası: {e} - Hata Anındaki Token: {self.peek()}")

                # Mevcut satırın sonuna atla
                while self.peek().type not in [TokenType.NEWLINE, TokenType.EOF]:
                    self.advance()
                self.skip_newlines()  # Yeni satırları atla

                # Eğer birden fazla hata oluştuysa, GUI sadece ilkini gösterebilir.
                # Ancak burada hatayı fırlatarak GUI'nin bunu yakalamasını sağlarız.
                # Normalde burada parser'ın bir sonraki statement'a devam etmesi gerekir.
                # Ancak biz GUI'de ilk hatayı görmek istediğimiz için ilk hatayı fırlatabiliriz.
                # Şimdilik, yakalanan hatayı GUI'ye iletmek için tekrar fırlatacağız.
                raise e  # Yakaladığımız ParserError'ı tekrar fırlat ki main.py yakalasın.

        return ProgramNode(statements)

    def skip_whitespace_and_comments(self):
        while True:
            if self.match(TokenType.NEWLINE):
                continue
            if self.match(TokenType.COMMENT):
                if self.check(TokenType.NEWLINE):
                    self.match(TokenType.NEWLINE)
                continue
            break

    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            pass

    def parse_statement(self):
        token = self.peek()

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

        if self.match(TokenType.OPERATOR) and self.previous().value == '=':
            if not isinstance(expr, VariableNode):
                raise ParserError(
                    f"Geçersiz atama hedefi. Değişken bekleniyor, ancak '{expr.__class__.__name__}' bulundu. (Satır {token.line})")
            return AssignmentNode(expr.name, self.parse_expression())

        return ExpressionStatementNode(expr)

    def parse_expression(self):
        # Basitlik adına, sadece karşılaştırma ve aritmetik işlemleri destekleyelim
        return self.parse_or_expression()

    def parse_comparison(self):
        expr = self.parse_term()  # Önceki mantıkla aynı: terimleri parse et
        ops = ['==', '!=', '<', '>', '<=', '>=']
        # Bu döngü hala doğru. Mantıksal operatörler daha düşük öncelikli olduğu için
        # parse_term (ve dolayısıyla parse_factor, parse_unary, parse_primary) önce çalışır.
        while self.check(TokenType.OPERATOR) and self.peek().value in ops:
            operator_token = self.advance()
            right = self.parse_term()
            expr = BinaryOpNode(expr, operator_token.value, right)
        return expr

    def parse_term(self):
        # Toplama ve Çıkarma
        expr = self.parse_factor()  # İlk olarak bir faktörü ayrıştır

        while self.check(TokenType.OPERATOR) and (self.peek().value == '+' or self.peek().value == '-'):
            operator = self.advance().value
            right = self.parse_factor()  # Operatörden sonra yine bir faktör beklenir
            expr = BinaryOpNode(expr, operator, right)
        return expr

    def parse_factor(self):
        # Çarpma ve Bölme
        expr = self.parse_unary()  # İlk olarak bir unary ifadeyi ayrıştır

        while self.check(TokenType.OPERATOR) and (self.peek().value == '*' or self.peek().value == '/'):
            operator = self.advance().value

            # BURADA KRİTİK NOKTA: Operatörden sonra bir 'ifade' beklenir.
            # 'sayi1 + *5' durumunda, '*' operatöründen sonra doğrudan '5' gelmeli.
            # Eğer '5' gelmezse veya '*' beklenmeyen bir konumdaysa, hata fırlatmalıyız.

            # advance() sonrası birincil ifadeyi ayrıştırmaya çalış
            right = self.parse_unary()  # Tekrar bir unary ifade bekliyoruz

            expr = BinaryOpNode(expr, operator, right)
        return expr

    def parse_unary(self):
        # Tekli operatörler (+, -)
        if self.check(TokenType.OPERATOR) and (self.peek().value == '+' or self.peek().value == '-'):
            operator = self.advance().value
            # Tekli operatörden sonra bir faktör beklenir.
            operand = self.parse_unary()  # Özyinelemeli olarak unary ifadeyi ayrıştır
            return UnaryOpNode(operator, operand)
        # Eğer bir unary operatör yoksa, birincil ifadeyi ayrıştır
        return self.parse_primary()

    def parse_primary(self):
        if self.match(TokenType.NUMBER):
            return NumberNode(float(self.previous().value))
        if self.match(TokenType.STRING):
            return StringNode(self.previous().value[1:-1])
        if self.match_keyword(TokenType.KEYWORD_TRUE):
            return BooleanNode(True)
        if self.match_keyword(TokenType.KEYWORD_FALSE):
            return BooleanNode(False)
        if self.match_keyword(TokenType.KEYWORD_NONE):
            return NoneNode()

        if self.check(TokenType.IDENTIFIER) or self.check_keyword(TokenType.KEYWORD_PRINT):
            name_token = self.advance()

            if self.match(TokenType.LPAREN):
                args = self.parse_arguments()
                self.consume(TokenType.RPAREN, ')')
                if name_token.type == TokenType.KEYWORD_PRINT:
                    return CallNode("print", args)
                return CallNode(name_token.value, args)

            return VariableNode(name_token.value)

        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, ')')
            return expr

        current_token = self.peek()
        raise ParserError(f"Beklenen bir ifade (sayı, string, değişken, parantezli ifade vb.) bulunamadı. "
                          f"Ancak '{current_token.value}' ({current_token.type.name}) bulundu. "
                          f"(Satır {current_token.line}, Sütun {current_token.column})")

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
        # Artık burada INDENT ve DEDENT tüketmiyoruz!
        # Bunlar parse_if_statement, parse_while_statement gibi metotlarda ele alınacak.

        self.skip_newlines()  # Önceki NEWLINE'ları atla

        # DEDENT veya EOF gelene kadar ifadeleri parse et
        while not (self.check(TokenType.DEDENT) or self.peek().type == TokenType.EOF):
            # Eğer boşluk veya yorum varsa atla (bu zaten iyi bir uygulama)
            self.skip_whitespace_and_comments()

            # Döngünün başında tekrar kontrol et
            if self.check(TokenType.DEDENT) or self.peek().type == TokenType.EOF:
                break

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

            # İfade sonunda NEWLINE'ları atla
            self.skip_newlines()

        return statements

    def parse_if_statement(self):
        self.consume(TokenType.KEYWORD_IF)  # 'if' tüket
        condition = self.parse_expression()
        self.consume(TokenType.COLON)  # ':' tüket
        self.consume(TokenType.NEWLINE)  # '\n' tüket

        self.consume(TokenType.INDENT)  # <-- BURADA INDENT tüket
        body = self.parse_block()  # Bloğu parse et
        self.consume(TokenType.DEDENT)  # <-- BURADA DEDENT tüket

        elif_clauses = []
        while self.check(TokenType.KEYWORD_ELIF):  # 'elif' tokenını kontrol et
            self.consume(TokenType.KEYWORD_ELIF)  # 'elif' tüket
            elif_condition = self.parse_expression()
            self.consume(TokenType.COLON)  # ':' tüket
            self.consume(TokenType.NEWLINE)  # '\n' tüket

            self.consume(TokenType.INDENT)  # <-- HER ELIF BLOĞU İÇİN INDENT tüket
            elif_body = self.parse_block()
            self.consume(TokenType.DEDENT)  # <-- HER ELIF BLOĞU İÇİN DEDENT tüket
            elif_clauses.append((elif_condition, elif_body))  # Veya IfNode'daki yapınıza göre ekleyin

        else_body = None
        if self.check(TokenType.KEYWORD_ELSE):  # 'else' tokenını kontrol et
            self.consume(TokenType.KEYWORD_ELSE)  # 'else' tüket
            self.consume(TokenType.COLON)  # ':' tüket
            self.consume(TokenType.NEWLINE)  # '\n' tüket

            self.consume(TokenType.INDENT)  # <-- ELSE BLOĞU İÇİN INDENT tüket
            else_body = self.parse_block()
            self.consume(TokenType.DEDENT)  # <-- ELSE BLOĞU İÇİN DEDENT tüket

        return IfNode(condition, body, elif_clauses, else_body)  # IfNode'unuza elif_clauses'ı da geçirin

    def parse_while_statement(self):
        self.consume_keyword(TokenType.KEYWORD_WHILE)
        condition = self.parse_expression()
        self.consume(TokenType.COLON, ':')
        self.consume(TokenType.NEWLINE)
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_or_expression(self):
        left = self.parse_and_expression()  # Daha yüksek öncelikli 'and' ifadesini parse et
        while self.check(TokenType.KEYWORD_OR):
            op_token = self.consume(TokenType.KEYWORD_OR)
            right = self.parse_and_expression()
            left = BinaryOpNode(left, op_token.value, right)  # operator olarak token.value kullanıyoruz
        return left

    def parse_and_expression(self):
        left = self.parse_not_expression()  # Daha yüksek öncelikli 'not' ifadesini parse et
        while self.check(TokenType.KEYWORD_AND):
            op_token = self.consume(TokenType.KEYWORD_AND)
            right = self.parse_not_expression()
            left = BinaryOpNode(left, op_token.value, right)
        return left

    def parse_not_expression(self):
        if self.check(TokenType.KEYWORD_NOT):
            op_token = self.consume(TokenType.KEYWORD_NOT)
            operand = self.parse_not_expression()  # not'ın sağındaki ifadeyi parse et (recursive)
            return UnaryOpNode(op_token.value, operand)  # operator olarak token.value kullanıyoruz
        else:
            return self.parse_comparison()  # Eğer 'not' yoksa, karşılaştırma ifadesini parse et

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

        # Hata mesajını daha da netleştirelim
        raise ParserError(f"Beklenen {expected_str} ancak bulundu: {actual.type.name} ('{actual.value}'). "
                          f"Token: {actual.type.name} ('{actual.value}') (Satır {actual.line}, Sütun {actual.column})")

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
