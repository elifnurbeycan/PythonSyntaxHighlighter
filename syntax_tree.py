# syntax_tree.py

class ASTNode:  # Eski 'Node' sınıfı, artık ana temel AST düğüm sınıfımız
    def _str_recursive(self, level, indent_char='  '):
        """
        AST düğümünün ve alt düğümlerinin girintili string temsilini döndürür.
        Bu metod her düğüm tipi için özelleştirilecektir.
        """
        prefix = indent_char * level
        # Varsayılan olarak sadece düğüm adını döndür (detaylar alt sınıflarda eklenecek)
        return f"{prefix}• {self.__class__.__name__}\n"

    def __repr__(self):
        # Varsayılan __repr__ olarak recursive str metodunu kullanabiliriz
        return self._str_recursive(0)


class ProgramNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, statements):
        self.statements = statements

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Program (ProgramNode)\n"
        if self.statements:
            s += f"{prefix}{indent_char}İfadeler:\n"
            for stmt in self.statements:
                s += stmt._str_recursive(level + 2, indent_char)
        return s


class AssignmentNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, identifier, expression):
        self.identifier = identifier  # Bu artık bir VariableNode olacak
        self.expression = expression

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Atama İfadesi (AssignmentNode)\n"
        s += f"{prefix}{indent_char}Değişken: '{self.identifier.name}'\n"  # identifier.name kullanıyoruz
        s += f"{prefix}{indent_char}Değer:\n"
        s += self.expression._str_recursive(level + 2, indent_char)
        return s


class ExpressionStatementNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, expression):
        self.expression = expression

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• İfade İfadesi (ExpressionStatementNode)\n"
        s += f"{prefix}{indent_char}İfade:\n"
        s += self.expression._str_recursive(level + 2, indent_char)
        return s


# IfNode zaten ASTNode'dan miras alıyordu, şimdi _str_recursive metodunu güncelleyelim
class IfNode(ASTNode):
    def __init__(self, condition, body, elif_clauses=None, else_body=None):
        self.condition = condition
        self.body = body  # List of statements
        self.elif_clauses = elif_clauses if elif_clauses is not None else []
        self.else_body = else_body  # List of statements or None

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Eğer İfadesi (IfNode)\n"
        s += f"{prefix}{indent_char}Koşul:\n"
        s += self.condition._str_recursive(level + 2, indent_char)
        s += f"{prefix}{indent_char}Eğer Doğruysa Çalışacak Blok (If Body):\n"
        if not self.body:  # Boş bloklar için
            s += f"{prefix}{indent_char * 2}(Boş Blok)\n"
        else:
            for stmt in self.body:
                s += stmt._str_recursive(level + 3, indent_char)

        if self.elif_clauses:
            s += f"{prefix}{indent_char}Diğer Eğer Blokları (Elif Clauses):\n"
            for idx, (elif_cond, elif_body) in enumerate(self.elif_clauses):
                s += f"{prefix}{indent_char * 2}Elif {idx + 1} Koşul:\n"
                s += elif_cond._str_recursive(level + 4, indent_char)
                s += f"{prefix}{indent_char * 2}Elif {idx + 1} Blok:\n"
                if not elif_body:  # Boş bloklar için
                    s += f"{prefix}{indent_char * 3}(Boş Blok)\n"
                else:
                    for stmt in elif_body:
                        s += stmt._str_recursive(level + 5, indent_char)

        if self.else_body:
            s += f"{prefix}{indent_char}Değilse Çalışacak Blok (Else Body):\n"
            if not self.else_body:  # Boş bloklar için
                s += f"{prefix}{indent_char * 2}(Boş Blok)\n"
            else:
                for stmt in self.else_body:
                    s += stmt._str_recursive(level + 3, indent_char)
        return s


class WhileNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Döngü İfadesi (WhileNode)\n"
        s += f"{prefix}{indent_char}Koşul:\n"
        s += self.condition._str_recursive(level + 2, indent_char)
        s += f"{prefix}{indent_char}Döngü Gövdesi (While Body):\n"
        if not self.body:
            s += f"{prefix}{indent_char * 2}(Boş Blok)\n"
        else:
            for stmt in self.body:
                s += stmt._str_recursive(level + 3, indent_char)
        return s


class FunctionDefNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Fonksiyon Tanımı (FunctionDefNode): '{self.name}'\n"
        s += f"{prefix}{indent_char}Parametreler: {', '.join(self.params) if self.params else '(Yok)'}\n"
        s += f"{prefix}{indent_char}Fonksiyon Gövdesi:\n"
        if not self.body:
            s += f"{prefix}{indent_char * 2}(Boş Blok)\n"
        else:
            for stmt in self.body:
                s += stmt._str_recursive(level + 3, indent_char)
        return s


class ReturnNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, expression=None):
        self.expression = expression

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Dönüş İfadesi (ReturnNode)\n"
        if self.expression:
            s += f"{prefix}{indent_char}Dönen Değer:\n"
            s += self.expression._str_recursive(level + 2, indent_char)
        else:
            s += f"{prefix}{indent_char}Dönen Değer: Yok (None)\n"
        return s


class CallNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, func_name, arguments):
        self.func_name = func_name
        self.arguments = arguments

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Fonksiyon Çağrısı (CallNode): '{self.func_name}'\n"
        if self.arguments:
            s += f"{prefix}{indent_char}Argümanlar:\n"
            for arg in self.arguments:
                s += arg._str_recursive(level + 2, indent_char)
        else:
            s += f"{prefix}{indent_char}Argümanlar: Yok\n"
        return s


class BinaryOpNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• İkili Operatör İfadesi (BinaryOpNode): '{self.operator}'\n"
        s += f"{prefix}{indent_char}Sol Operand:\n"
        s += self.left._str_recursive(level + 2, indent_char)
        s += f"{prefix}{indent_char}Sağ Operand:\n"
        s += self.right._str_recursive(level + 2, indent_char)
        return s


class UnaryOpNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        s = f"{prefix}• Tekli Operatör İfadesi (UnaryOpNode): '{self.operator}'\n"
        s += f"{prefix}{indent_char}Operand:\n"
        s += self.operand._str_recursive(level + 2, indent_char)
        return s


class NumberNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, value):
        self.value = value

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        return f"{prefix}• Sayı Değeri (NumberNode): {self.value}\n"


class StringNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, value):
        self.value = value

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        # String değeri tırnak işaretleri olmadan saklandığı varsayıldı
        return f"{prefix}• Metin Değeri (StringNode): \"{self.value}\"\n"


class VariableNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, name):
        self.name = name

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        return f"{prefix}• Değişken (VariableNode): '{self.name}'\n"


class BooleanNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self, value):
        self.value = value

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        return f"{prefix}• Mantıksal Değer (BooleanNode): {self.value}\n"


class NoneNode(ASTNode):  # ASTNode'dan miras alıyor
    def __init__(self):
        pass

    def _str_recursive(self, level, indent_char='  '):
        prefix = indent_char * level
        return f"{prefix}• Boş Değer (NoneNode): None\n"
