# syntax_tree.py
class Node:
    def __repr__(self):
        return f"{self.__class__.__name__}"


class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode(statements={self.statements})"


class AssignmentNode(Node):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return f"(Assign {self.identifier} = {self.expression})"


class ExpressionStatementNode(Node):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"(ExprStmt {self.expression})"

class IfNode(Node):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body  # Liste
        self.else_body = else_body or [] # Liste (elif kaldırıldı)

    def __repr__(self):
        else_str = f" else={self.else_body}" if self.else_body else ""
        return f"IfNode(condition={self.condition}, body={self.body}{else_str})"


class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileNode(condition={self.condition}, body={self.body})"

# ForNode kaldırıldı

class FunctionDefNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FunctionDefNode(name={self.name}, params={self.params}, body={self.body})"


class ReturnNode(Node):
    def __init__(self, expression=None):
        self.expression = expression

    def __repr__(self):
        return f"ReturnNode({self.expression})"


class CallNode(Node):
    def __init__(self, func_name, arguments):
        self.func_name = func_name
        self.arguments = arguments

    def __repr__(self):
        return f"CallNode(func={self.func_name}, args={self.arguments})"

class BinaryOpNode(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.operator} {self.right})"


class UnaryOpNode(Node):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"({self.operator}{self.operand})"


class NumberNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class StringNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'"{self.value}"'


class VariableNode(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class BooleanNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

class NoneNode(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "None"

# PassNode, BreakNode, ContinueNode kaldırıldı
