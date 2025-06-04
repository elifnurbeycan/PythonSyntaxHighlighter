import re

class Token:
    def __init__(self, type, value, start_index, end_index):
        self.type = type
        self.value = value
        self.start_index = start_index  # "line.column" formatında
        self.end_index = end_index

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.start_index} -> {self.end_index})"

class Lexer:
    def __init__(self):
        self.token_specs = [
            ('KEYWORD',    r'\b(if|else|while|for|def|return|True|False|None|continue|break|print|in|range)\b'),
            ('OPERATOR',   r'==|!=|<=|>=|<|>|=|\+|-|\*|/|%|\(|\)|\[|\]|\{|\}|:|,|\.'),
            ('STRING',     r'"[^"\n]*"|\'[^\'\n]*\''),
            ('NUMBER',     r'\b\d+(\.\d*)?\b|\b\.\d+\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('COMMENT',    r'#.*'),
            ('WHITESPACE', r'[ \t]+'),
            ('MISMATCH',   r'.'),
        ]
        self.token_regex = re.compile('|'.join(f"(?P<{name}>{pattern})" for name, pattern in self.token_specs))

    def tokenize(self, code):
        tokens = []
        lines = code.splitlines()

        for line_number, line in enumerate(lines, start=1):
            pos = 0
            while pos < len(line):
                match = self.token_regex.match(line, pos)
                if not match:
                    break
                kind = match.lastgroup
                value = match.group(kind)
                start_idx = f"{line_number}.{pos}"
                end_idx = f"{line_number}.{pos + len(value)}"
                if kind not in ['WHITESPACE']:
                    tokens.append(Token(kind, value, start_idx, end_idx))
                pos = match.end()

        return tokens