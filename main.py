import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from lexer import Lexer
from parser import Parser, ParserError
from tokens import TokenType


class SyntaxHighlighterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Real-Time Syntax Highlighter with AST")

        # Initialize components
        self.lexer = Lexer()
        self.setup_ui()
        self.setup_tags()
        self.setup_autocomplete()

        # Initial code and highlight
        self.text_area.insert("1.0",
                              "# Sample code\nx = 10\nif x > 5 then\n  print \"Greater\"\nelse\n  print \"Smaller\"\nendif")
        self.highlight_syntax()

    def setup_ui(self):
        # Text area
        self.text_area = ScrolledText(self.master, wrap="word", width=80, height=20,
                                      font=("Consolas", 12))
        self.text_area.pack(padx=10, pady=(10, 0), fill=tk.BOTH, expand=True)

        # AST output
        self.ast_output = ScrolledText(self.master, height=10, font=("Consolas", 10),
                                       bg="#f0f0f0", state=tk.DISABLED)
        self.ast_output.pack(padx=10, pady=(5, 10), fill=tk.BOTH)
        self.ast_output.insert("1.0", "Abstract Syntax Tree:\n")

        # Error label
        self.error_label = tk.Label(self.master, text="", fg="red")
        self.error_label.pack()

        # Bind events
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<Tab>", self.insert_spaces)

    def setup_tags(self):
        # Configure tag colors
        tag_colors = {
            "keyword": "blue",
            "operator": "red",
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
            'print', 'if', 'else', 'while', 'for',
            'then', 'endif', 'endwhile', 'and', 'or'
        ]

    def on_key_release(self, event=None):
        # Debounce mechanism for better performance
        if hasattr(self, '_after_id'):
            self.master.after_cancel(self._after_id)
        self._after_id = self.master.after(300, self.highlight_syntax)

    def highlight_syntax(self):
        code = self.text_area.get("1.0", tk.END)

        # Clear previous tags
        for tag in self.text_area.tag_names():
            if tag not in ['sel', 'insert']:
                self.text_area.tag_remove(tag, "1.0", tk.END)

        try:
            # Tokenize and highlight
            tokens = self.lexer.tokenize(code)
            for token in tokens:
                if token.line is None or token.column is None:
                    continue

                start = f"{token.line}.{token.column}"
                end = f"{token.line}.{token.column + len(str(token.value))}"

                tag_name = token.type.name.lower()
                if tag_name in self.text_area.tag_names():
                    self.text_area.tag_add(tag_name, start, end)

            # Parse and show AST
            parser = Parser(tokens)
            ast = parser.parse()
            self.update_ast_output(ast)
            self.show_error("")  # Clear error if successful

        except Exception as e:
            self.show_error(f"Error: {str(e)}")
            self.update_ast_output([f"❌ Error: {str(e)}"])

    def update_ast_output(self, ast_nodes):
        self.ast_output.config(state=tk.NORMAL)
        self.ast_output.delete("1.0", tk.END)
        self.ast_output.insert("1.0", "Abstract Syntax Tree:\n\n")

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
        # Basic autocomplete implementation
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
