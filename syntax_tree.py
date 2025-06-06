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

class ASTNode:
    pass

class IfNode(ASTNode):
    def __init__(self, condition, body, elif_clauses=None, else_body=None): # <-- elif_clauses eklendi
        self.condition = condition
        self.body = body # List of statements
        self.elif_clauses = elif_clauses if elif_clauses is not None else [] # list of (condition, body) tuples or ElifClauseNode objects
        self.else_body = else_body # List of statements or None

    def __repr__(self):
        # Temsili biraz daha karmaşıklaşabilir
        if_str = f"IfNode(Condition={self.condition}, Body={self.body}"
        if self.elif_clauses:
            if_str += f", ElifClauses={self.elif_clauses}"
        if self.else_body:
            if_str += f", ElseBody={self.else_body}"
        if_str += ")"
        return if_str

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
