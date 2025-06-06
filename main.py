# main.py
import tkinter as tk
from tkinter import scrolledtext
from lexer import Lexer
from parser import Parser, ParserError
from tokens import TokenType
from syntax_tree import *

class SyntaxHighlighterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Python Syntax Highlighter")

        self.lexer = Lexer()
        self.parser = Parser([])  # Başlangıçta boş token listesi ile oluştur

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.line_numbers = tk.Text(self.main_frame, width=4, padx=3, pady=3, takefocus=0,
                                    border=0, background='#f0f0f0', state='disabled',
                                    wrap='none', font=("Consolas", 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD,
                                                   font=("Consolas", 10),
                                                   undo=True)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.error_label = tk.Label(master, text="", fg="white", bg="lightgreen")
        self.error_label.pack(side=tk.TOP, fill=tk.X, pady=2)

        # AST çıktısı ve hata mesajları için Text widget'ı, başlangıçta DISABLED
        self.ast_output = scrolledtext.ScrolledText(master, wrap=tk.WORD,
                                                    font=("Consolas", 10),
                                                    height=15, state='disabled')
        self.ast_output.pack(fill=tk.BOTH, expand=True)

        self.define_tags()

        self.text_area.bind("<<Modified>>", self.on_text_modified)
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<MouseWheel>", self.on_text_scroll)
        self.text_area.bind("<Button-4>", self.on_text_scroll)
        self.text_area.bind("<Button-5>", self.on_text_scroll)

        # text_area'nın kaydırma çubuğunu hem kendi yview'ine hem de line_numbers'ın yview'ine bağla
        self.text_area.vbar.config(command=self.yview_text_and_numbers)

        self.update_line_numbers()  # Başlangıçta satır numaralarını oluştur

        self.text_area.edit_modified(False)
        self.highlight_syntax()  # Başlangıçta sözdizimini vurgula

        # ---KAYDIRMA METODLARI ---

    def update_line_numbers(self):
        """
        text_area'daki satır sayısına göre satır numaralarını günceller.
        """
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", tk.END)

        line_count = int(self.text_area.index('end-1c').split('.')[0])

        # Her satır için numara ekle
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        # Satır numarası alanını, ana metin alanının kaydırma konumuna eşitle
        self.line_numbers.yview_moveto(self.text_area.yview()[0])
        self.line_numbers.config(state='disabled')

    def define_tags(self):
        # Genişletilmiş renk tag'leri listesi, highlight_syntax ile tam uyumlu
        self.text_area.tag_config("keyword", foreground="#0000FF")  # Mavi (if, else, while, def, return için)
        self.text_area.tag_config("operator", foreground="#FF8C00")  # Turuncu (+, -, *, /, =, ==, >, < vb.)
        self.text_area.tag_config("number", foreground="#8B0000")  # Koyu Kırmızı (Sayılar için)
        self.text_area.tag_config("string", foreground="#008000")  # Yeşil (Metinler için)
        self.text_area.tag_config("comment", foreground="#808080",
                                  font=("Consolas", 10, "italic"))  # Gri ve İtalik (# yorumlar için)

        self.text_area.tag_config("identifier", foreground="#000000")  # Siyah (Varsayılan tanımlayıcılar için)
        self.text_area.tag_config("variable", foreground="#333333")  # Koyu Gri (Değişken isimleri için)
        self.text_area.tag_config("function_call", foreground="#8A2BE2")  # Mor (print gibi fonksiyon çağrıları için)
        self.text_area.tag_config("boolean", foreground="#FF00FF")  # Magenta (True, False, None için)
        self.text_area.tag_config("lparen", foreground="#8B008B")  # Koyu Mor (( ) için)
        self.text_area.tag_config("rparen", foreground="#8B008B")  # Koyu Mor (( ) için)
        self.text_area.tag_config("colon", foreground="#8B008B")  # Koyu Mor (: için)
        self.text_area.tag_config("comma", foreground="#8B008B")  # Koyu Mor (, için)
        self.text_area.tag_config("mismatch", foreground="red",
                                  background="yellow")  # Tanınmayan karakterler için (uyarı)

        # Hata işaretleyici tag'leri
        self.text_area.tag_config("error_line", background="#FFCCCC", underline=True)
        self.text_area.tag_config("error_char", background="#FF9999", foreground="red")

    def on_text_modified(self, event=None):
        if self.text_area.edit_modified():
            self.highlight_syntax()
            self.update_line_numbers()
            self.text_area.edit_modified(False)

    def on_key_release(self, event):
        self.highlight_syntax()
        self.update_line_numbers()

    def on_text_scroll(self, event):
        self.update_line_numbers()

    def yview_text_area(self, *args):
        self.text_area.yview_moveto(args[0])
        self.update_line_numbers()

    def yview_text_and_numbers(self, *args):
        """
        hem text_area'yı hem de satır numaralarını senkronize olarak kaydırır.
        """
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)
        self.update_line_numbers()  # Kaydırma sonrası satır numaralarını güncelle

    def highlight_syntax(self):
        code = self.text_area.get("1.0", tk.END)

        for tag in self.text_area.tag_names():
            if tag not in ['sel', 'insert']:
                self.text_area.tag_remove(tag, "1.0", tk.END)

        try:
            tokens = self.lexer.tokenize(code)

            # Syntax Vurgulama
            for token in tokens:
                # NEWLINE, INDENT, DEDENT, EOF gibi görsel olarak renklendirilmeyen token'ları atla
                if token.type in [TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT, TokenType.EOF,
                                  TokenType.WHITESPACE]:
                    continue  # WHITESPACE'i de atla

                # Token'ın satır ve sütun bilgisi yoksa atla (olmamalı ama önlem)
                if token.line is None or token.column is None:
                    continue

                start = f"{token.line}.{token.column}"
                end = f"{token.line}.{token.column + len(str(token.value))}"

                # Token tipine göre doğru tag'i belirle ve uygula
                if token.type in [TokenType.KEYWORD_IF, TokenType.KEYWORD_ELSE,
                                  TokenType.KEYWORD_WHILE, TokenType.KEYWORD_DEF,
                                  TokenType.KEYWORD_RETURN]:
                    self.text_area.tag_add("keyword", start, end)
                elif token.type == TokenType.KEYWORD_PRINT:
                    self.text_area.tag_add("function_call", start, end)
                elif token.type in [TokenType.KEYWORD_TRUE, TokenType.KEYWORD_FALSE,
                                    TokenType.KEYWORD_NONE]:
                    self.text_area.tag_add("boolean", start, end)
                elif token.type == TokenType.OPERATOR:
                    self.text_area.tag_add("operator", start, end)
                elif token.type == TokenType.NUMBER:
                    self.text_area.tag_add("number", start, end)
                elif token.type == TokenType.STRING:
                    self.text_area.tag_add("string", start, end)
                elif token.type == TokenType.COMMENT:
                    self.text_area.tag_add("comment", start, end)
                elif token.type == TokenType.IDENTIFIER:
                    self.text_area.tag_add("variable", start, end)  # Tanımlayıcılar için 'variable' tag'ını kullan
                elif token.type == TokenType.LPAREN:
                    self.text_area.tag_add("lparen", start, end)
                elif token.type == TokenType.RPAREN:
                    self.text_area.tag_add("rparen", start, end)
                elif token.type == TokenType.COLON:
                    self.text_area.tag_add("colon", start, end)
                elif token.type == TokenType.COMMA:
                    self.text_area.tag_add("comma", start, end)
                elif token.type == TokenType.MISMATCH:
                    self.text_area.tag_add("mismatch", start, end)
                # Başka bir token tipi varsa ve renklendirmek isterseniz buraya ekleyin
                # else:
                #     print(f"Uyarı: {token.type.name} için tanımlı renk tag'i yok.") # Teşhis için

            # AST Oluşturma ve Gösterme
            parser = Parser(tokens)
            ast = parser.parse()
            self.update_ast_output(ast)

            # --- Hata yoksa: Yeşil renk ve "Kod Hatasız!" mesajı ---
            self.show_error("Kod Hatasız!", color="green")

        except ParserError as e:
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Parser Hatası: {str(e)}\n\n")
            self.ast_output.config(state=tk.DISABLED)
            self.show_error(f"Parser Hatası: {e}", color="red")

        except Exception as e:
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Genel Hata: {str(e)}\n\n")
            import traceback
            error_details = traceback.format_exc(limit=1).strip().split('\n')[-1]
            self.ast_output.insert(tk.END, f"Detaylar: {error_details}\n")
            self.ast_output.config(state=tk.DISABLED)
            self.show_error(f"Genel Hata: {str(e)}", color="red")

    def update_ast_output(self, ast_nodes):
        self.ast_output.config(state=tk.NORMAL)
        self.ast_output.delete("1.0", tk.END)
        self.ast_output.insert("1.0", "Abstract Syntax Tree:\n\n")

        def print_node(node, indent_level=0):  # <-- Burası 'indent_level' olarak tanımlanmış, doğru.
            indent_str = "  " * indent_level
            self.ast_output.insert(tk.END, f"{indent_str}• {node.__class__.__name__}")

            if isinstance(node, ProgramNode):
                # ...
                for stmt in node.statements:
                    print_node(stmt, indent_level + 1)

            elif isinstance(node, AssignmentNode):
                # ...
                print_node(node.expression, indent_level + 1)

            elif isinstance(node, ExpressionStatementNode):
                # ...
                print_node(node.expression, indent_level + 1)

            elif isinstance(node, IfNode):
                # ...
                self.ast_output.insert(tk.END, f"{indent_str}  Condition:\n")
                print_node(node.condition, indent_level + 2)
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)
                if node.else_body:
                    self.ast_output.insert(tk.END, f"{indent_str}  Else Body:\n")
                    for stmt in node.else_body:
                        print_node(stmt, indent_level + 2)

            elif isinstance(node, WhileNode):
                # ...
                self.ast_output.insert(tk.END, f"{indent_str}  Condition:\n")
                print_node(node.condition, indent_level + 2)
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)

            elif isinstance(node, FunctionDefNode):
                # ...
                self.ast_output.insert(tk.END, f"{indent_str}  Params: {', '.join(node.params)}\n")
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)

            elif isinstance(node, ReturnNode):
                # ...
                if node.expression:
                    print_node(node.expression, indent_level + 1)

            elif isinstance(node, CallNode):
                # ...
                self.ast_output.insert(tk.END, f"{indent_str}  Args:\n")
                for arg in node.arguments:
                    print_node(arg, indent_level + 2)

            elif isinstance(node, BinaryOpNode):
                # ...
                print_node(node.left, indent_level + 1)
                print_node(node.right, indent_level + 1)

            elif isinstance(node, UnaryOpNode):
                # ...
                print_node(node.operand, indent_level + 1)

        # Ana AST düğümünü yazdırmaya başla (ProgramNode beklenir)
        if isinstance(ast_nodes, ProgramNode):
            print_node(ast_nodes)
        else:
            self.ast_output.insert(tk.END, f"• {ast_nodes.__class__.__name__}: {ast_nodes}\n")

        self.ast_output.config(state=tk.DISABLED)
        self.ast_output.see(tk.END)

    def show_error(self, message, color="green"):
        self.error_label.config(text=message, fg="white", bg=color)

        if color == "red":
            if hasattr(self, '_error_clear_job') and self._error_clear_job is not None:
                self.master.after_cancel(self._error_clear_job)
            self._error_clear_job = None  # Hata varken otomatik temizleme yok

        # Eğer mesaj "Kod Hatasız!" ise veya başka yeşil bir mesaj ise belirli bir süre sonra temizle
        elif color == "green" or not message:
            # Eğer önceki bir 'after' zamanlaması varsa onu iptal et (hatadan yeşile geçerse).
            if hasattr(self, '_error_clear_job') and self._error_clear_job is not None:
                self.master.after_cancel(self._error_error_clear_job)

            # Yeşil mesajlar için 2 saniye sonra temizle
            self._error_clear_job = self.master.after(2000, lambda: self.error_label.config(text="", bg="lightgreen"))

        # Eğer mesaj temizleniyorsa (message boşsa), önceki job'u iptal et ve arka planı temizle
        if not message and hasattr(self, '_error_clear_job') and self._error_clear_job is not None:
            self.master.after_cancel(self._error_clear_job)
            self._error_clear_job = None
            self.error_label.config(bg="lightgreen")

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
    root = tk.Tk()
    app = SyntaxHighlighterGUI(root)
    root.mainloop()
