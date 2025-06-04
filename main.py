import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from lexer import Lexer

class SyntaxHighlighterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Python Syntax Highlighter")

        self.text_area = ScrolledText(master, wrap="word", width=80, height=25,
                                      font=("Consolas", 12))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.lexer = Lexer()

        # Renk etiketleri
        self.text_area.tag_configure('keyword', foreground='blue')
        self.text_area.tag_configure('operator', foreground='orange')
        self.text_area.tag_configure('number', foreground='green')
        self.text_area.tag_configure('string', foreground='red')
        self.text_area.tag_configure('comment', foreground='gray')
        self.text_area.tag_configure('mismatch', foreground='purple')
        self.text_area.tag_configure('identifier', foreground='black')

        # Tuş bırakıldığında tetiklenecek
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)

        # İlk örnek kod
        initial_code = """# Python Sözdizimi Vurgulayıcı
if x == 10:
    y = "Merhaba Dünya" + str(x) # Dize ve sayılar
    print(y * 2 / 5.5)
else:
    for i in range(10):
        if i < 5:
            continue
    z = True
    return None
"""
        self.text_area.insert(tk.END, initial_code)
        self.highlight_syntax()

    def highlight_syntax(self, event=None):
        # Önceki etiketleri temizle
        for tag in self.text_area.tag_names():
            if tag not in ['sel', 'insert']:
                self.text_area.tag_remove(tag, "1.0", tk.END)

        code = self.text_area.get("1.0", tk.END)
        tokens = self.lexer.tokenize(code)

        for token in tokens:
            start_index = token.start_index
            end_index = token.end_index

            if token.type == 'KEYWORD':
                self.text_area.tag_add('keyword', start_index, end_index)
            elif token.type == 'OPERATOR':
                self.text_area.tag_add('operator', start_index, end_index)
            elif token.type == 'NUMBER':
                self.text_area.tag_add('number', start_index, end_index)
            elif token.type == 'STRING':
                self.text_area.tag_add('string', start_index, end_index)
            elif token.type == 'COMMENT':
                self.text_area.tag_add('comment', start_index, end_index)
            elif token.type == 'MISMATCH':
                self.text_area.tag_add('mismatch', start_index, end_index)
            elif token.type == 'IDENTIFIER':
                self.text_area.tag_add('identifier', start_index, end_index)

def main():
    root = tk.Tk()
    gui = SyntaxHighlighterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()