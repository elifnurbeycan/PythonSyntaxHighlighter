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

        # Hata mesajı etiketi - arka plan rengini de kontrol edeceğiz
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

        # self.initial_code = """...""" ve insert satırları kaldırıldı
        self.text_area.edit_modified(False)
        self.highlight_syntax()  # Başlangıçta sözdizimini vurgula

        # ---KAYDIRMA METODLARI ---

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
            self.update_line_numbers()
            self.text_area.edit_modified(False)

    def on_key_release(self, event):
        self.highlight_syntax()
        self.update_line_numbers()

    def on_text_scroll(self, event):
        self.update_line_numbers()

    def yview_text_area(self, *args):
        # Line numbers'ın kaydırma çubuğu hareket ettiğinde (ki olmayacak, ama yine de) metin alanını kaydır
        self.text_area.yview_moveto(args[0])
        self.update_line_numbers()

    def yview_text_and_numbers(self, *args):
        """
        hem text_area'yı hem de satır numaralarını senkronize olarak kaydırır.
        """
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)
        self.update_line_numbers()  # Kaydırma sonrası satır numaralarını güncelle

    def update_line_numbers(self):
        """
        text_area'daki satır sayısına göre satır numaralarını günceller.
        """
        self.line_numbers.config(state='normal')  # Yazmak için etkinleştir
        self.line_numbers.delete("1.0", tk.END)  # Tüm mevcut satır numaralarını sil

        # text_area'daki satır sayısını al
        line_count = int(self.text_area.index('end-1c').split('.')[0])

        # Her satır için numara ekle
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        # Satır numarası alanını, ana metin alanının kaydırma konumuna eşitle
        self.line_numbers.yview_moveto(self.text_area.yview()[0])
        self.line_numbers.config(state='disabled')  # Yazma bittikten sonra tekrar devre dışı bırak


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

    def highlight_syntax(self):
        code = self.text_area.get("1.0", tk.END)

        for tag in self.text_area.tag_names():
            if tag not in ['sel', 'insert']:
                self.text_area.tag_remove(tag, "1.0", tk.END)

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
            self.update_ast_output(ast)  # Geçerli AST'yi gönderiyoruz

            # --- Hata yoksa: Yeşil renk ve "Kod Hatasız!" mesajı ---
            self.show_error("Kod Hatasız!", color="green")

        except ParserError as e:
            # Parser hatasında AST çıktısını temizle ve hata mesajını göster
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Parser Hatası: {str(e)}\n\n")
            self.ast_output.config(state=tk.DISABLED)
            # --- Hata varsa: Kırmızı renk ve hata mesajı ---
            self.show_error(f"Parser Hatası: {e}", color="red")

        except Exception as e:
            # Diğer genel hatalarda AST çıktısını temizle ve hata mesajını göster
            self.ast_output.config(state=tk.NORMAL)
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert("1.0", f"❌ Genel Hata: {str(e)}\n\n")
            import traceback
            error_details = traceback.format_exc(limit=1).strip().split('\n')[-1]
            self.ast_output.insert(tk.END, f"Detaylar: {error_details}\n")
            self.ast_output.config(state=tk.DISABLED)
            # --- Diğer hatalar varsa: Kırmızı renk ve hata mesajı ---
            self.show_error(f"Genel Hata: {str(e)}", color="red")

    # update_ast_output metodu (Sınıfın doğrudan bir metodu olmalı)
    def update_ast_output(self, ast_nodes):
        self.ast_output.config(state=tk.NORMAL)  # Yazmak için etkinleştir
        self.ast_output.delete("1.0", tk.END)
        self.ast_output.insert("1.0", "Abstract Syntax Tree:\n\n")

        # print_node fonksiyonu, update_ast_output metodunun içinde tanımlanmıştır.
        # Bu fonksiyon, AST düğümlerini özyinelemeli olarak yazdırır.
        def print_node(node, indent_level=0):
            indent_str = "  " * indent_level
            # Başlangıçta düğümün sınıf adını yazdır
            self.ast_output.insert(tk.END, f"{indent_str}• {node.__class__.__name__}")

            # Düğüm tipine göre detayları ekle
            if isinstance(node, ProgramNode):
                self.ast_output.insert(tk.END, "(statements=[")
                if node.statements:
                    # İlk statement'ın tipini göster, ardından '...' eğer birden fazlaysa
                    self.ast_output.insert(tk.END, f"{node.statements[0].__class__.__name__}")
                if len(node.statements) > 1:
                    self.ast_output.insert(tk.END, ", ...")
                self.ast_output.insert(tk.END, "])\n")
                for stmt in node.statements:
                    print_node(stmt, indent_level + 1)

            elif isinstance(node, AssignmentNode):
                # identifier ve expression kullanılıyor
                self.ast_output.insert(tk.END,
                                       f"(identifier='{node.identifier}', expression={node.expression.__class__.__name__})\n")
                print_node(node.expression, indent_level + 1)

            elif isinstance(node, ExpressionStatementNode):
                self.ast_output.insert(tk.END, f"(expression={node.expression.__class__.__name__})\n")
                print_node(node.expression, indent_level + 1)

            elif isinstance(node, IfNode):
                self.ast_output.insert(tk.END,
                                       f"(condition={node.condition.__class__.__name__}, body=[...], else=[...])\n")
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
                self.ast_output.insert(tk.END, f"(condition={node.condition.__class__.__name__}, body=[...])\n")
                self.ast_output.insert(tk.END, f"{indent_str}  Condition:\n")
                print_node(node.condition, indent_level + 2)
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)

            elif isinstance(node, FunctionDefNode):
                # name, params, body kullanılıyor
                self.ast_output.insert(tk.END, f"(name='{node.name}', params={node.params}, body=[...])\n")
                self.ast_output.insert(tk.END, f"{indent_str}  Params: {', '.join(node.params)}\n")
                self.ast_output.insert(tk.END, f"{indent_str}  Body:\n")
                for stmt in node.body:
                    print_node(stmt, indent_level + 2)

            elif isinstance(node, ReturnNode):
                # expression kullanılıyor
                self.ast_output.insert(tk.END,
                                       f"(expression={node.expression.__class__.__name__ if node.expression else 'None'})\n")
                if node.expression:  # expression null olabilir
                    print_node(node.expression, indent_level + 1)

            elif isinstance(node, CallNode):
                # func_name ve arguments kullanılıyor
                self.ast_output.insert(tk.END, f"(func='{node.func_name}', args=[...])\n")
                self.ast_output.insert(tk.END, f"{indent_str}  Args:\n")
                for arg in node.arguments:  # arguments kullanıldı
                    print_node(arg, indent_level + 2)

            elif isinstance(node, BinaryOpNode):
                # left, operator, right kullanılıyor
                self.ast_output.insert(tk.END,
                                       f"(left={node.left.__class__.__name__}, operator='{node.operator}', right={node.right.__class__.__name__})\n")
                print_node(node.left, indent_level + 1)
                print_node(node.right, indent_level + 1)

            elif isinstance(node, UnaryOpNode):
                # operator, operand kullanılıyor
                self.ast_output.insert(tk.END,
                                       f"(operator='{node.operator}', operand={node.operand.__class__.__name__})\n")
                print_node(node.operand, indent_level + 1)

            elif isinstance(node, NumberNode):
                # value kullanılıyor
                self.ast_output.insert(tk.END, f"({node.value})\n")

            elif isinstance(node, StringNode):
                # value kullanılıyor
                self.ast_output.insert(tk.END, f"(\"{node.value}\")\n")

            elif isinstance(node, VariableNode):
                # name kullanılıyor
                self.ast_output.insert(tk.END, f"('{node.name}')\n")

            elif isinstance(node, BooleanNode):
                # value kullanılıyor
                self.ast_output.insert(tk.END, f"({node.value})\n")

            elif isinstance(node, NoneNode):
                self.ast_output.insert(tk.END, "(None)\n")

            else:
                # Tanımsız bir düğüm türü gelirse, genel bir temsilini yazdır.
                # __repr__ metodunun düzgün çalıştığından emin olmak için bu faydalıdır.
                self.ast_output.insert(tk.END, f"({node.__class__.__name__} object)\n")

        # Ana AST düğümünü yazdırmaya başla (ProgramNode beklenir)
        if isinstance(ast_nodes, ProgramNode):
            print_node(ast_nodes)
        else:
            # Eğer ast_nodes bir ProgramNode değilse, doğrudan yazdır.
            # Bu genellikle tek bir ifadeyi test ederken veya parser tam bir ProgramNode döndürmediğinde olur.
            self.ast_output.insert(tk.END, f"• {ast_nodes.__class__.__name__}: {ast_nodes}\n")

        self.ast_output.config(state=tk.DISABLED)  # Yazma bittikten sonra devre dışı bırak
        self.ast_output.see(tk.END)  # En son satırı göster (kaydırma için)

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

    def show_error(self, message, color="green"):  # Renk parametresi eklendi, varsayılan yeşil
        self.error_label.config(text=message, fg="white", bg=color)  # Metin beyaz, arka plan renkli
        # Hata mesajı boş değilse 5 saniye sonra temizle (sadece yeşil mesajlar için belki kaldırmalı?)
        # Ya da hata mesajı varsa ve kırmızı ise temizleme, yeşil ise temizle gibi bir mantık eklenebilir.
        # Şimdilik, hata mesajı varsa (kırmızı veya yeşil) her zaman gösterelim.
        # Eğer yeşil "Kod Hatasız!" mesajını bir süre sonra kaybolmasını isterseniz, aşağıdaki satırı etkin bırakabilirsiniz:
        # if message and color == "green":
        #     self.master.after(5000, lambda: self.error_label.config(text="", bg="lightgray")) # 5 saniye sonra temizle ve gri yap


def main():
    root = tk.Tk()
    app = SyntaxHighlighterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = SyntaxHighlighterGUI(root) # Eğer sınıfınızın adı buysa
    root.mainloop()
