# parser.py
from tokens import TokenType, Token
from syntax_tree import *

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.lookahead = None  # Sonraki anlamlı tokenı tutacak
        self._prime_lookahead()  # lookahead'i başlat

    def _prime_lookahead(self):
        # self.current'ı boşluk ve yorum tokenlarının ötesine ilerlet
        while self.current < len(self.tokens) and \
                (self.tokens[self.current].type == TokenType.WHITESPACE or \
                 self.tokens[self.current].type == TokenType.COMMENT):
            self.current += 1

        # Eğer token listesinin sonuna gelinmediyse lookahead'i ayarla
        if self.current < len(self.tokens):
            self.lookahead = self.tokens[self.current]
        else:
            # Listenin sonundaysak, bir EOF (End Of File) tokenı döndür
            # Satır ve sütun bilgisini de ekleyebiliriz, ancak -1, -1 yeterli olur
            self.lookahead = Token(TokenType.EOF, '', -1, -1)

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
        # --- Diğer Statement Türleri (if, while, def, return vb.) ---
        if self.check_keyword(TokenType.KEYWORD_IF):
            return self.parse_if_statement()
        elif self.check_keyword(TokenType.KEYWORD_WHILE):
            return self.parse_while_statement()
        elif self.check_keyword(TokenType.KEYWORD_DEF):
            return self.parse_function_def()
        elif self.check_keyword(TokenType.KEYWORD_RETURN):
            return self.parse_return_statement()
        elif self.check_keyword(TokenType.KEYWORD_IMPORT):
            return self.parse_import_statement()
        elif self.check_keyword(TokenType.KEYWORD_FROM):
            return self.parse_from_import_statement()
        elif self.check_keyword(TokenType.KEYWORD_PASS):
            # Basit bir pass statement'ı
            self.advance()  # 'pass' keyword'ünü tüket
            return ExpressionStatementNode(NoneNode())  # PassNode() da olabilir

        # --- Atama İfadesi veya Normal İfade İfadesi ---
        # Parser'ın mevcut durumunu (ham token indeksi ve lookahead tokenı) kaydet.
        # Bu, ileriye bakma işlemi için geçici olarak durumu değiştirebilmemizi sağlar.
        original_current_raw_index = self.current
        original_lookahead_token = self.lookahead

        # Eğer mevcut token bir IDENTIFIER ise, bu bir atamanın başlangıcı olabilir.
        if self.check(TokenType.IDENTIFIER):
            # Geçici olarak IDENTIFIER'ı tüket ve lookahead'i bir sonraki anlamlı tokene getir.
            # self.advance() çağrısı, self.current'ı ilerletir ve _prime_lookahead'i çağırarak self.lookahead'i günceller.
            temp_identifier_token = self.advance()

            # Şimdi, yeni lookahead tokenı (yani IDENTIFIER'dan sonraki token) bir ASSIGN mı?
            if self.check(TokenType.ASSIGN):
                # Evet, bir atama ifadesi bulduk!
                # Parser'ın durumunu, atama işlemini baştan doğru bir şekilde ayrıştırmak için ilk haline geri döndür.
                self.current = original_current_raw_index
                self.lookahead = original_lookahead_token

                # Atama deyimini ayrıştırmak için özel metodu çağır.
                return self.parse_assignment_statement()
            else:
                # IDENTIFIER'dan sonra ASSIGN yoktu (örn: bir fonksiyon çağrısı, tek başına bir değişken).
                # Parser'ın durumunu geri döndür ve bu satırı normal bir ifade deyimi olarak ayrıştırmaya devam et.
                self.current = original_current_raw_index
                self.lookahead = original_lookahead_token

        # Eğer yukarıdaki koşullar bir atama ifadesine uymadıysa (ya IDENTIFIER ile başlamıyorsa ya da ASSIGN takip etmiyorsa),
        # bu satır basit bir ifade deyimi olmalıdır.
        expr = self.parse_expression()
        return ExpressionStatementNode(expr)

    def parse_assignment_statement(self):
        # consume metoduna ikinci parametre olarak beklenen değeri GİRMEYİN.
        # Bu, consume metodunun TokenType.IDENTIFIER türünde herhangi bir IDENTIFIER'ı kabul etmesini sağlar.
        identifier_token = self.consume(TokenType.IDENTIFIER)  # <-- Sadece TokenType.IDENTIFIER gönderin!
        variable_node = VariableNode(identifier_token.value)

        self.consume(TokenType.ASSIGN,
                     "=")  # Burada '=' değeri göndermek mantıklı, çünkü ASSIGN tokenının değeri genelde hep '='dır.

        expression = self.parse_expression()
        return AssignmentNode(variable_node, expression)

    def parse_expression(self):
        # Basitlik adına, sadece karşılaştırma ve aritmetik işlemleri destekleyelim
        return self.parse_or_expression()

    def parse_comparison(self):
        expr = self.parse_term()
        # Operatörler listesi (string değerleriyle)
        # ops = ['==', '!=', '<', '>', '<=', '>='] # Buna artık gerek yok

        while self.check(TokenType.EQ) or self.check(TokenType.NE) or \
                self.check(TokenType.LT) or self.check(TokenType.GT) or \
                self.check(TokenType.LE) or self.check(TokenType.GE):
            operator_token = self.advance()
            right = self.parse_term()
            expr = BinaryOpNode(expr, operator_token.value, right)
        return expr

    def parse_term(self):
        # Toplama ve Çıkarma
        expr = self.parse_factor()

        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            operator_token = self.advance()
            right = self.parse_factor()
            expr = BinaryOpNode(expr, operator_token.value, right)
        return expr

    def parse_factor(self):
        # Çarpma, Bölme ve Mod
        expr = self.parse_unary()  # İlk olarak bir unary ifadeyi ayrıştır

        while self.check(TokenType.MULTIPLY) or \
                self.check(TokenType.DIVIDE) or \
                self.check(TokenType.MODULO):

            operator = self.advance().value
            right = self.parse_unary()
            expr = BinaryOpNode(expr, operator, right)
        return expr

    def parse_unary(self):
        if self.check(TokenType.PLUS) or self.check(TokenType.MINUS):  # Check specific token types PLUS/MINUS
            operator = self.advance().value
            operand = self.parse_unary()
            return UnaryOpNode(operator, operand)
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

    def consume(self, type_, message=None):
        token = self.peek()
        if token.type == type_ and (
                message is None or token.value == message):  # message'ı expected_value olarak kullanın
            self.advance()
            return token

        raise ParserError(f"Beklenen '{message if message else type_.name}' bulunamadı. "
                          f"Ancak '{token.value}' ({token.type.name}) bulundu. "
                          f"(Satır {token.line}, Sütun {token.column})")

    def consume_keyword(self, keyword_type):
        if self.check_keyword(keyword_type):
            return self.advance()
        actual = self.peek()
        raise ParserError(
            f"Beklenen anahtar kelime {keyword_type.name} ancak bulundu: {actual.type.name} ('{actual.value}') (Satır {actual.line}, Sütun {actual.column})")

    def check(self, type_, value_to_check=None):
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
        # Eğer dosyanın sonundaysak, EOF tokenı döndür (bu durumda ilerleme olmaz)
        if self.is_at_end():
            return Token(TokenType.EOF, '', -1, -1)

            # Mevcut lookahead tokenını kaydet (bu, az önce işlenecek olan token)
        previous_token = self.lookahead

        # self.current'ı bir sonraki raw tokene ilerlet
        self.current += 1

        # Yeni lookahead'i belirlemek için _prime_lookahead'i çağır
        # Bu, otomatik olarak boşluk ve yorumları atlayacaktır.
        self._prime_lookahead()

        # Az önce işlenen tokenı döndür
        return previous_token

    def previous(self):
        return self.tokens[self.current - 1]

    def peek(self):
        return self.lookahead

    def is_at_end(self):
        # Lookahead tokenının EOF olup olmadığını kontrol et
        return self.lookahead.type == TokenType.EOF
