# main.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from lexer import Lexer
from parser import Parser, ParserError
from tokens import TokenType
from syntax_tree import *


class SyntaxHighlighterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simplified Python Syntax Highlighter with AST")

        self.lexer = Lexer()
        self.setup_ui()
        self.setup_tags()
        self.setup_autocomplete()

        initial_code = """
# Bu bir Python yorum satırı
sayi = 5
if sayi == 5:
    print("Sayı 5'e eşit.")
else:
    print("Sayı 5'ten küçük.")

def topla(a, b):
    sonuc = a + b
    return sonuc

x = topla(10, 20)
print(x)
"""
        self.text_area.insert("1.0", initial_code)
        self.highlight_syntax()

    def setup_ui(self):
        self.text_area = ScrolledText(self.master, wrap="word", width=80, height=20,
                                      font=("Consolas", 12))
        self.text_area.pack(padx=10, pady=(10, 0), fill=tk.BOTH, expand=True)

        self.ast_output = ScrolledText(self.master, height=10, font=("Consolas", 10),
                                       bg="#f0f0f0", state=tk.DISABLED)
        self.ast_output.pack(padx=10, pady=(5, 10), fill=tk.BOTH)
        self.ast_output.insert("1.0", "Abstract Syntax Tree:\n")

        self.error_label = tk.Label(self.master, text="", fg="red")
        self.error_label.pack()

        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<Tab>", self.insert_spaces)

    def setup_tags(self):
        tag_colors = {
            "keyword_if": "blue", "keyword_else": "blue",
            "keyword_while": "blue", "keyword_def": "blue",
            "keyword_return": "blue", "keyword_true": "blue",
            "keyword_false": "blue", "keyword_none": "blue",
            "keyword_print": "blue",

            "operator": "red",  # Tüm operatörler tek bir etiket altında
            "lparen": "darkred", "rparen": "darkred",
            "colon": "darkred", "comma": "darkred",

            "number": "green",
            "string": "#008800",
            "comment": "gray",
            "identifier": "black",
            "mismatch": "purple"
        }

        for tag, color in tag_colors.items():
            self.text_area.tag_configure(tag, foreground=color)

    def setup_autocomplete(self):
        self.autocomplete_list = [
            'if', 'else', 'while', 'def', 'return', 'True', 'False', 'None', 'print'
        ]

    def on_key_release(self, event=None):
        if hasattr(self, '_after_id'):
            self.master.after_cancel(self._after_id)
        self._after_id = self.master.after(300, self.highlight_syntax)

    def highlight_syntax(self):
        code = self.text_area.get("1.0", tk.END)

        for tag in self.text_area.tag_names():
            if tag not in ['sel', 'insert']:
                self.text_area.tag_remove(tag, "1.0", tk.END)

        self.show_error("")  # Önceki hataları temizle
        self.ast_output.config(state=tk.NORMAL)
        self.ast_output.delete("1.0", tk.END)
        self.ast_output.insert("1.0", "Abstract Syntax Tree:\n")
        self.ast_output.config(state=tk.DISABLED)

        try:
            tokens = self.lexer.tokenize(code)

            # Syntax Vurgulama
            for token in tokens:
                if token.line is None or token.column is None:
                    continue

                tag_name = token.type.name.lower()

                start = f"{token.line}.{token.column}"
                end = f"{token.line}.{token.column + len(str(token.value))}"

                if tag_name in self.text_area.tag_names():
                    self.text_area.tag_add(tag_name, start, end)
                elif token.type == TokenType.OPERATOR:  # Genel operatör etiketi
                    self.text_area.tag_add('operator', start, end)
                elif token.type == TokenType.MISMATCH:  # Hatalı token'ları vurgula
                    self.text_area.tag_add('mismatch', start, end)

            # AST Oluşturma ve Gösterme
            parser = Parser(tokens)
            ast = parser.parse()
            self.update_ast_output(ast)
            # Eğer parser hata fırlatmadıysa ama bir hata mesajı yazdıysa
            if "Parser Hatası:" in self.ast_output.get("1.0", tk.END):
                self.show_error("Parser tamamlandı, ancak hatalar bulundu (AST çıktısına bakınız).")


        except ParserError as e:  # Sadece ParserError'ı yakala
            self.show_error(f"❌ Parser Hatası: {str(e)}")
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Parser Hatası: {str(e)}\n\n")
            self.ast_output.insert(tk.END, "Daha fazla detay için PyCharm konsolunu kontrol edin.\n")
            self.ast_output.config(state=tk.DISABLED)

        except Exception as e:  # Diğer genel hataları yakala
            self.show_error(f"❌ Uygulama Hatası: {str(e)}")
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Uygulama Hatası: {str(e)}\n\n")
            import traceback
            error_details = traceback.format_exc(limit=1).strip().split('\n')[-1]
            self.ast_output.insert(tk.END, f"Details: {error_details}\n")
            self.ast_output.config(state=tk.DISABLED)

    def update_ast_output(self, ast_nodes):
        self.ast_output.config(state=tk.NORMAL)
        self.ast_output.delete("1.0", tk.END)
        self.ast_output.insert("1.0", "Abstract Syntax Tree:\n\n")

        def print_node(node, indent_level=0):
            indent_str = "  " * indent_level
            self.ast_output.insert(tk.END, f"{indent_str}• {node}\n")

            if isinstance(node, ProgramNode):
                for stmt in node.statements:
                    print_node(stmt, indent_level + 1)
            elif isinstance(node, AssignmentNode):
                print_node(node.expression, indent_level + 1)
            elif isinstance(node, ExpressionStatementNode):
                print_node(node.expression, indent_level + 1)
            elif isinstance(node, IfNode):
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)
                if node.else_body:
                    self.ast_output.insert(tk.END, f"{indent_str}  Else Body:\n")
                    for stmt in node.else_body:
                        print_node(stmt, indent_level + 2)
            elif isinstance(node, WhileNode):
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)
            elif isinstance(node, FunctionDefNode):
                self.ast_output.insert(tk.END, f"{indent_str}  Params: {node.params}\n")
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)
            elif isinstance(node, ReturnNode) and node.expression:
                print_node(node.expression, indent_level + 1)
            elif isinstance(node, CallNode):
                self.ast_output.insert(tk.END, f"{indent_str}  Args:\n")
                for arg in node.arguments:
                    print_node(arg, indent_level + 2)
            elif isinstance(node, BinaryOpNode):
                print_node(node.left, indent_level + 1)
                print_node(node.right, indent_level + 1)
            elif isinstance(node, UnaryOpNode):
                print_node(node.operand, indent_level + 1)

        if isinstance(ast_nodes, ProgramNode):
            print_node(ast_nodes)
        else:
            for node in ast_nodes:
                self.ast_output.insert(tk.END, f"• {node}\n")

        self.ast_output.config(state=tk.DISABLED)
        self.ast_output.see(tk.END)

    def show_error(self, message):
        self.error_label.config(text=message)
        if message:
            self.master.after(5000, lambda: self.error_label.config(text=""))

    def insert_spaces(self, event):
        self.text_area.insert(tk.INSERT, "    ")
        return "break"

    def auto_complete(self, event):
        word = self.text_area.get("insert-1c wordstart", "insert-1c wordend")
        matches = [w for w in self.autocomplete_list if w.startswith(word)]

        if len(matches) == 1:
            self.text_area.delete("insert-1c wordstart", "insert-1c wordend")
            self.text_area.insert("insert", matches[0])
        return "break"


def main():
    root = tk.Tk()
    app = SyntaxHighlighterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
