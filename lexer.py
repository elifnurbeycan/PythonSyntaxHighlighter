import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}', line={self.line}, col={self.column})"

class Lexer:
    def __init__(self):
        self.token_specs = [
            ('KEYWORD',    r'\b(if|else|while|for|def|return|True|False|None|continue|break)\b'),
            ('OPERATOR',   r'==|!=|<=|>=|<|>|=|!|\+|-|\*|/|%|\(|\)|\[|\]|\{|\}|:|,|\.'),
            ('STRING',     r'(\".*?\"|\'.*?\')'),
            ('NUMBER',     r'\b\d+(\.\d*)?|\.\d+\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('COMMENT',    r'#.*'),
            ('NEWLINE',    r'\n'),
            ('SKIP',       r'[ \t]+'),
            ('MISMATCH',   r'.'),
        ]

        self.token_regex = re.compile('|'.join(f"(?P<{name}>{pattern})" for name, pattern in self.token_specs))

    def tokenize(self, code):
        tokens = []
        line_num = 1
        line_start = 0

        for mo in self.token_regex.finditer(code):
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - line_start

            if kind == 'NEWLINE':
                line_num += 1
                line_start = mo.end()
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                tokens.append(Token(kind, value, line_num, column))
                print(f"Tanımsız karakter: {value!r} satır {line_num}, sütun {column}")
            else:
                tokens.append(Token(kind, value, line_num, column))

        return tokens
