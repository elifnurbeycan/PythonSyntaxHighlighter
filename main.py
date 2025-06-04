import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from lexer import Lexer

class SyntaxHighlighterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Python Syntax Highlighter")

        self.text_area = ScrolledText(master, wrap="word", width=80, height=25, font=("Consolas", 12))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.lexer = Lexer()

        # Renk tanımlamaları
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("operator", foreground="orange")
        self.text_area.tag_configure("number", foreground="green")
        self.text_area.tag_configure("string", foreground="red")
        self.text_area.tag_configure("comment", foreground="gray")
        self.text_area.tag_configure("identifier", foreground="black")
        self.text_area.tag_configure("mismatch", foreground="purple")

        # Olaylar
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<Tab>", self.insert_spaces)

        # Başlangıç kodu
        initial_code = """# Python Syntax Highlighter Example
if x == 10:
    y = "Hello, World!" + str(x)  # String and numbers
    print(y * 2 / 5.5)            # Operators and float
else:
    for i in range(10):
        if i < 5:
            continue
    z = True
    return None
"""
        self.text_area.insert("1.0", initial_code)
        self.highlight_syntax()

    def insert_spaces(self, event):
        self.text_area.insert(tk.INSERT, "    ")  # 4 boşluk
        return "break"

    def highlight_syntax(self, event=None):
        # Önce tüm önceki etiketleri kaldır
        for tag in self.text_area.tag_names():
            if tag not in ("sel", "insert"):
                self.text_area.tag_remove(tag, "1.0", tk.END)

        code = self.text_area.get("1.0", tk.END)
        tokens = self.lexer.tokenize(code)

        for token in tokens:
            if token.line is None or token.column is None:
                continue

            start_index = f"{token.line}.{token.column}"
            end_index = f"{token.line}.{token.column + len(token.value)}"

            self.text_area.tag_add(token.type.lower(), start_index, end_index)

def main():
    root = tk.Tk()
    app = SyntaxHighlighterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
