import re
import tkinter as tk
import customtkinter as ctk


# Python keyword sets for syntax highlighting
_KW = set("and as assert async await break class continue def del elif else "
          "except finally for from global if import in is lambda nonlocal not "
          "or pass raise return try while with yield".split())
_BUILTIN = set("print len range int str float list dict set tuple bool type "
               "input open map filter zip enumerate sorted min max sum abs "
               "round isinstance hasattr getattr setattr True False None self".split())


class MarkdownRenderer:
    """Parses markdown and creates formatted widgets with rich text."""

    def render(self, parent, text, bubble_bg=None):
        self._bubble_bg = bubble_bg or "#f0f4f8"
        for block in self._parse(text):
            self._render_block(parent, block)

    # ---- Parsing ----

    def _parse(self, text):
        blocks = []
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]

            if line.strip().startswith('```'):
                lang = line.strip()[3:].strip()
                code = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1
                blocks.append({'type': 'code', 'lang': lang, 'text': '\n'.join(code)})
                continue

            m = re.match(r'^(#{1,6})\s+(.+)', line)
            if m:
                blocks.append({'type': 'heading', 'level': len(m.group(1)), 'text': m.group(2)})
                i += 1
                continue

            if '|' in line and line.strip().startswith('|'):
                tbl = []
                while i < len(lines) and '|' in lines[i]:
                    tbl.append(lines[i])
                    i += 1
                blocks.append({'type': 'table', 'lines': tbl})
                continue

            m = re.match(r'^(\s*)[*\-+]\s+(.+)', line)
            if m:
                blocks.append({'type': 'list', 'text': m.group(2), 'indent': len(m.group(1))})
                i += 1
                continue

            m = re.match(r'^(\s*)\d+\.\s+(.+)', line)
            if m:
                blocks.append({'type': 'nlist', 'text': m.group(2), 'indent': len(m.group(1))})
                i += 1
                continue

            if not line.strip():
                i += 1
                continue

            para = []
            while (i < len(lines) and lines[i].strip()
                   and not lines[i].strip().startswith('```')
                   and not re.match(r'^#{1,6}\s', lines[i])
                   and not (lines[i].strip().startswith('|') and '|' in lines[i][1:])
                   and not re.match(r'^\s*[*\-+]\s+', lines[i])
                   and not re.match(r'^\s*\d+\.\s+', lines[i])):
                para.append(lines[i])
                i += 1
            blocks.append({'type': 'para', 'text': ' '.join(para)})
        return blocks

    # ---- Rendering ----

    def _render_block(self, parent, block):
        t = block['type']
        if t == 'code':
            self._code(parent, block)
        elif t == 'heading':
            self._heading(parent, block)
        elif t == 'table':
            self._table(parent, block)
        elif t in ('list', 'nlist'):
            self._list_item(parent, block)
        elif t == 'para':
            self._para(parent, block)

    def _para(self, parent, block):
        """Render paragraph with inline bold, italic, code."""
        text = block['text'].strip()
        if not text:
            return
        self._rich_label(parent, text, size=13)

    def _heading(self, parent, block):
        sizes = {1: 20, 2: 17, 3: 15, 4: 14, 5: 13, 6: 12}
        size = sizes.get(block['level'], 14)
        self._rich_label(parent, block['text'], size=size, bold=True,
                         color="#1e293b", pady=(8, 3))

    def _list_item(self, parent, block):
        indent = block.get('indent', 0) // 2
        prefix = "  " * indent + "•  "
        self._rich_label(parent, prefix + block['text'], size=13,
                         padx=(8 + indent * 12, 4), pady=2)

    def _rich_label(self, parent, text, size=13, bold=False, color=None,
                    padx=4, pady=3):
        """Create a text widget with inline bold/italic/code support."""
        bg = self._get_bg(parent)

        tw = tk.Text(parent, wrap="word", relief="flat",
                     bg=bg, borderwidth=0, highlightthickness=0,
                     padx=2, pady=2)

        base_font = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
        fg = color or "#334155"

        tw.configure(font=base_font, fg=fg)
        tw.tag_configure("bold", font=("Segoe UI", size, "bold"), foreground="#1e293b")
        tw.tag_configure("italic", font=("Segoe UI", size, "italic"))
        tw.tag_configure("code", font=("Consolas", size - 1),
                         background="#e2e8f0", foreground="#7c3aed")

        # Parse inline formatting
        parts = re.split(r'(\*\*.*?\*\*|\*[^*]+?\*|`[^`]+?`)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                tw.insert("end", part[2:-2], "bold")
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                tw.insert("end", part[1:-1], "italic")
            elif part.startswith('`') and part.endswith('`'):
                tw.insert("end", f" {part[1:-1]} ", "code")
            else:
                tw.insert("end", part)

        tw.configure(state="disabled")
        lines = int(tw.index("end-1c").split(".")[0])
        tw.configure(height=max(lines, 1))
        tw.pack(fill="x", padx=padx, pady=pady)

    def _code(self, parent, block):
        """Render code block with syntax highlighting and copy button."""
        frame = ctk.CTkFrame(parent, fg_color="#1e1e2e", corner_radius=8)
        frame.pack(fill="x", pady=6, padx=2)

        # Header bar
        hdr = ctk.CTkFrame(frame, fg_color="#161b22", corner_radius=0)
        hdr.pack(fill="x", padx=1, pady=(1, 0))

        if block['lang']:
            ctk.CTkLabel(hdr, text=block['lang'],
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color="#8b949e").pack(side="left", padx=10, pady=4)

        code_text = block['text']
        ctk.CTkButton(
            hdr, text="📋 Copy code", width=90, height=22, corner_radius=4,
            font=ctk.CTkFont(size=10), fg_color="transparent",
            hover_color="#2a2a3e", text_color="#8b949e",
            command=lambda: self._copy(parent, code_text)
        ).pack(side="right", padx=6, pady=4)

        # Code text widget with syntax highlighting
        tw = tk.Text(frame, wrap="none", relief="flat",
                     bg="#1e1e2e", fg="#e6edf3",
                     font=("Consolas", 12), borderwidth=0,
                     highlightthickness=0, padx=10, pady=8,
                     insertbackground="#e6edf3")

        # Syntax color tags
        tw.tag_configure("keyword", foreground="#569cd6")
        tw.tag_configure("builtin", foreground="#c586c0")
        tw.tag_configure("string", foreground="#ce9178")
        tw.tag_configure("comment", foreground="#6a9955")
        tw.tag_configure("number", foreground="#b5cea8")
        tw.tag_configure("decorator", foreground="#dcdcaa")
        tw.tag_configure("function", foreground="#dcdcaa")

        tw.insert("1.0", code_text)
        self._highlight_syntax(tw)

        lines = code_text.count('\n') + 1
        tw.configure(height=min(lines, 30), state="disabled")
        tw.pack(fill="x", padx=8, pady=(0, 8))

    def _highlight_syntax(self, tw):
        """Apply basic syntax highlighting to code in a Text widget."""
        content = tw.get("1.0", "end")

        # Comments (# ...)
        for m in re.finditer(r'#[^\n]*', content):
            self._tag_range(tw, m, "comment")

        # Strings (single and double quoted)
        for m in re.finditer(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')', content):
            self._tag_range(tw, m, "string")

        # Numbers
        for m in re.finditer(r'\b\d+\.?\d*\b', content):
            self._tag_range(tw, m, "number")

        # Keywords
        for m in re.finditer(r'\b(' + '|'.join(_KW) + r')\b', content):
            self._tag_range(tw, m, "keyword")

        # Builtins
        for m in re.finditer(r'\b(' + '|'.join(_BUILTIN) + r')\b', content):
            self._tag_range(tw, m, "builtin")

        # Decorators
        for m in re.finditer(r'@\w+', content):
            self._tag_range(tw, m, "decorator")

        # Function definitions
        for m in re.finditer(r'(?<=def )\w+', content):
            self._tag_range(tw, m, "function")

    def _tag_range(self, tw, match, tag):
        """Apply a tag to a regex match in a Text widget."""
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        tw.tag_add(tag, start, end)

    def _table(self, parent, block):
        rows = []
        for line in block['lines']:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(set(c) <= {'-', ':', ' '} for c in cells):
                continue
            rows.append(cells)
        if not rows:
            return

        tf = ctk.CTkFrame(parent, fg_color="#f1f5f9", corner_radius=8)
        tf.pack(fill="x", pady=4, padx=2)

        raw = '\n'.join(block['lines'])
        ctk.CTkButton(
            tf, text="📋 Copy table", width=90, height=22, corner_radius=4,
            font=ctk.CTkFont(size=10), fg_color="transparent",
            hover_color="#e2e8f0", text_color="#64748b",
            command=lambda: self._copy(parent, raw)
        ).pack(anchor="e", padx=8, pady=(4, 0))

        grid = ctk.CTkFrame(tf, fg_color="transparent")
        grid.pack(fill="x", padx=6, pady=(2, 6))

        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                is_hdr = (r == 0)
                ctk.CTkLabel(
                    grid, text=self._clean_inline(cell),
                    font=ctk.CTkFont(size=12, weight="bold" if is_hdr else "normal"),
                    fg_color="#e2e8f0" if is_hdr else "transparent",
                    text_color="#1e293b",
                    corner_radius=4, anchor="w"
                ).grid(row=r, column=c, sticky="ew", padx=2, pady=1,
                       ipadx=6, ipady=3)
            for c in range(len(row)):
                grid.grid_columnconfigure(c, weight=1)

    def _clean_inline(self, text):
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        return text

    def _get_bg(self, widget):
        """Get background color from parent widget chain."""
        try:
            bg = widget.cget("fg_color")
            if isinstance(bg, (list, tuple)):
                return bg[0]
            if bg and bg != "transparent":
                return bg
        except Exception:
            pass
        return "#f0f4f8"

    def _copy(self, widget, text):
        widget.clipboard_clear()
        widget.clipboard_append(text)
