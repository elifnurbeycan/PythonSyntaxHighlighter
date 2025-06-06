# Real-Time Grammar-Based Syntax Highlighter with GUI

## 📌 Overview

This project is a **real-time syntax highlighter** with a **graphical user interface (GUI)**, developed as part of a Programming Languages course. It performs **lexical analysis** and **syntax parsing** based on a formally defined grammar, without using any external syntax highlighting libraries.

The system highlights **at least 5 distinct token types in real-time**, demonstrating both **lexical** and **syntax analysis** in an interactive environment. It also includes a custom-built **parser** and **lexer**, developed fully from scratch.

## 🚀 Features

- ✅ Real-time syntax highlighting with live GUI updates
- ✅ At least 5 token types highlighted with distinct styles
- ✅ Lexer built using a state diagram & program implementation
- ✅ Top-down parser (pre-order traversal of parse tree)
- ✅ Formal grammar definition and custom tokenization
- ✅ Publicly shared demo video and technical article

## 🔧 Technologies Used

- **Language:** Python
- **GUI Framework:** Tkinter
- **Lexer Method:** State Diagram & Programmatic Implementation
- **Parser Type:** Top-Down Recursive Descent Parser
- **Token Types:** Keywords, Identifiers, Operators, Numbers, Symbols

## 🧠 Syntax Analysis

### Lexical Analyzer

- Built using a state diagram and implemented in Python.
- Tokenizes input based on regular expressions for:
  - **Keywords** (e.g., `if`, `while`, `return`)
  - **Identifiers** (variable/function names)
  - **Operators** (`+`, `-`, `=`, etc.)
  - **Literals** (numbers)
  - **Symbols** (`{`, `}`, `(`, `)`, etc.)

### Syntax Analyzer

- Implements a **Top-Down Parser** using a **recursive descent strategy**.
- Parses tokens based on a **context-free grammar** defined for the target language.
- Detects and reports syntax errors live in the GUI.

## 🎨 Highlighting Scheme

| Token Type   | Color         |
|--------------|---------------|
| Keyword      | Blue          |
| Identifier   | Black         |
| Number       | Dark Orange   |
| Operator     | Red           |
| Symbol       | Gray          |

## 🖼 GUI Implementation

The GUI is developed using **Tkinter** and supports:

- Real-time highlighting as the user types
- Color-coded token display
- Error highlighting for invalid syntax
- AST (Abstract Syntax Tree) display panel (optional enhancement)

## 📄 Documentation

All major decisions and implementations are described in the [project article](#link-to-article).

Documentation includes:

- Grammar definition and design decisions
- Lexical analyzer architecture
- Parser methodology and grammar rules
- Highlighting logic and color scheme
- GUI structure and user experience goals

## 📹 Demo Video

Watch the project demo on YouTube:  
👉 [Click to Watch Demo](#link-to-video)

## 📚 Article

Read the full write-up covering design choices and implementation:  
📝 [Read the Article](#link-to-article)

## 📦 Installation & Usage

```bash
# Clone the repository
git clone https://github.com/elifnurbeycan/PythonSyntaxHighlighter.git
cd realtime-syntax-highlighter

# Run the application
python main.py
