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

        # Lexer ve Parser başlat
        self.lexer = Lexer()
        self.parser = Parser([])  # Başlangıçta boş token listesi

        # Ana çerçeve
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Satır Numaraları İçin Yeni Bölüm Başlangıcı
        self.line_numbers = tk.Text(self.main_frame, width=4, padx=3, pady=3, takefocus=0,
                                    border=0, background='#f0f0f0', state='disabled',
                                    wrap='none', font=("Consolas", 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        # Satır Numaraları İçin Yeni Bölüm Sonu

        # Metin alanı (ScrolledText kullanmaya devam)
        self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD,
                                                   font=("Consolas", 10),
                                                   undo=True)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Hata mesajı etiketi
        self.error_label = tk.Label(master, text="", fg="red")
        self.error_label.pack(side=tk.TOP, fill=tk.X, pady=2)

        # AST çıktısı alanı
        self.ast_output = scrolledtext.ScrolledText(master, wrap=tk.WORD,
                                                    font=("Consolas", 10),
                                                    height=15, state='disabled')
        self.ast_output.pack(fill=tk.BOTH, expand=True)

        # Etiket stillerini tanımla
        self.define_tags()

        # Metin alanındaki değişiklikleri izle
        self.text_area.bind("<<Modified>>", self.on_text_modified)

        # --- Satır Numaralarını Güncellemek İçin Bindings (DÜZELTME BAŞLANGICI) ---
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<MouseWheel>", self.on_text_scroll)  # Windows/Linux
        self.text_area.bind("<Button-4>", self.on_text_scroll)  # MacOS (Scroll Up)
        self.text_area.bind("<Button-5>", self.on_text_scroll)  # MacOS (Scroll Down)

        # İki metin alanının kaydırma çubuklarını birbirine bağlama
        # text_area'nın dikey kaydırma çubuğu hareket ettiğinde line_numbers'ı kaydır
        self.text_area.vbar.config(command=self.yview_all)  # Yeni yview_all metodunu kullanacağız

        # line_numbers için ayrı bir kaydırma çubuğu yoktur, sadece text_area'nın scrollbar'ını takip eder.
        # Bu yüzden aşağıdaki satır kaldırıldı:
        # self.line_numbers.vbar['command'] = self.yview_text_area

        self.update_line_numbers()  # Başlangıçta satır numaralarını oluştur
        # --- Satır Numaralarını Güncellemek İçin Bindings (DÜZELTME SONU) ---


        self.text_area.edit_modified(False)  # Modified flag'ı temizle
        self.highlight_syntax()  # Başlangıçta sözdizimini vurgula

        # --- YENİ veya GÜNCELLENMİŞ KAYDIRMA METODLARI ---

    def yview_all(self, *args):
        # Hem metin alanını hem de satır numaralarını senkronize olarak kaydır
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)
        self.update_line_numbers()  # Kaydırma sonrası satır numaralarını güncelle

        # on_text_scroll ve on_key_release zaten update_line_numbers'ı çağırıyor, bu iyi.
        # Diğer yview metodlarını (yview_line_numbers ve yview_text_area) artık doğrudan kullanmayacağız
        # ama yine de kodda bırakıp çağrılmadıklarından emin olabilirsiniz, veya silebilirsiniz.
        # Sadece yview_all metodunu kullanacağız.

    def update_line_numbers(self):
        # Satır numaralarını güncelleyen ana metod
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", tk.END)

        # Mevcut kodunuzdaki line_count hesaplama mantığını koruyorum
        line_count = int(self.text_area.index('end-1c').split('.')[0])

        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        # Ana metin alanının kaydırma konumunu takip et
        self.line_numbers.yview_moveto(self.text_area.yview()[0])
        self.line_numbers.config(state='disabled')

    def define_tags(self):
        # ... (bu metod aynı kalacak)
        self.text_area.tag_config("keyword", foreground="#0000FF")  # Mavi
        self.text_area.tag_config("identifier", foreground="#000000")  # Siyah
        self.text_area.tag_config("number", foreground="#FF0000")  # Kırmızı
        self.text_area.tag_config("string", foreground="#008000")  # Yeşil
        self.text_area.tag_config("operator", foreground="#FF4500")  # Turuncu
        self.text_area.tag_config("lparen", foreground="#8B008B")  # Koyu Mor
        self.text_area.tag_config("rparen", foreground="#8B008B")  # Koyu Mor
        self.text_area.tag_config("colon", foreground="#8B008B")  # Koyu Mor
        self.text_area.tag_config("comma", foreground="#8B008B")  # Koyu Mor
        self.text_area.tag_config("comment", foreground="#808080", font=("Consolas", 10, "italic"))  # Gri ve İtalik

    def on_text_modified(self, event=None):
        if self.text_area.edit_modified():
            self.highlight_syntax()
            self.update_line_numbers()  # Satır numaralarını da güncelle
            self.text_area.edit_modified(False)

    def on_key_release(self, event):
        # Her tuşa basıldığında satır numaralarını ve sözdizimini güncelle
        self.highlight_syntax()
        self.update_line_numbers()

    def on_text_scroll(self, event):
        # Metin alanı kaydırıldığında satır numaralarını güncelle
        self.update_line_numbers()

    def yview_line_numbers(self, *args):
        # Metin alanının kaydırma çubuğu hareket ettiğinde satır numaralarını da kaydır
        self.line_numbers.yview_moveto(args[0])
        self.update_line_numbers()

    def yview_text_area(self, *args):
        # Line numbers'ın kaydırma çubuğu hareket ettiğinde (ki olmayacak, ama yine de) metin alanını kaydır
        self.text_area.yview_moveto(args[0])
        self.update_line_numbers()

    def update_line_numbers(self):
        # Satır numaralarını güncelleyen ana metod
        self.line_numbers.config(state='normal')  # Düzenlemeyi etkinleştir
        self.line_numbers.delete("1.0", tk.END)  # Mevcut numaraları sil

        # Metin alanının ilk ve son görünen satırlarını al
        first_visible_line, last_visible_line = self.text_area.yview()
        start_line_index = int(self.text_area.index(f"@{0},{0}").split('.')[0])  # Görünür alanın başlangıç satırı
        end_line_index = int(self.text_area.index(tk.END).split('.')[0])  # Toplam satır sayısı

        # Görünür alana göre satır numaralarını ekle
        line_count = int(self.text_area.index('end-1c').split('.')[0])

        # Sadece görünen satırları değil, tüm satırları numaralandırmak daha kolay ve doğru olur
        # Çünkü kaydırma çubuğu ile tüm satırlar numaralandırılmalı.
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        # Metin alanıyla satır numaralarını senkronize et
        self.line_numbers.yview_moveto(self.text_area.yview()[0])
        self.line_numbers.config(state='disabled')  # Tekrar düzenlemeyi devre dışı bırak

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
                elif token.type == TokenType.OPERATOR and 'operator' in self.text_area.tag_names():
                    self.text_area.tag_add('operator', start, end)

            # AST Oluşturma ve Gösterme
            parser = Parser(tokens)
            ast = parser.parse()
            self.update_ast_output(ast)
            self.show_error("")  # Hata yoksa hata mesajını temizle


        except ParserError as e:
            self.show_error(f"Parser Hatası: {e}")
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Parser Hatası: {str(e)}\n\n")
            self.ast_output.config(state=tk.DISABLED)
        except Exception as e:
            self.show_error(f"Genel Hata: {str(e)}")
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Hata: {str(e)}\n\n")
            import traceback
            error_details = traceback.format_exc(limit=1).strip().split('\n')[-1]
            self.ast_output.insert(tk.END, f"Detaylar: {error_details}\n")
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
    root = tk.Tk()
    app = SyntaxHighlighterGUI(root) # Eğer sınıfınızın adı buysa
    root.mainloop()
