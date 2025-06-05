class Node:
    pass


class AssignmentNode(Node):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return f"(assign {self.identifier} = {self.expression})"


class PrintNode(Node):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"(print {self.expression})"


class IfNode(Node):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body          # Girintili blok
        self.else_body = else_body or []  # Else bloğu (opsiyonel)

    def __repr__(self):
        return f"IfNode(condition={self.condition}, body={self.body}, else={self.else_body})"


class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"(while {self.condition} do {self.body})"


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