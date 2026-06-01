"""Convert 报告.md to PDF using Markdown + fpdf2 (pure Python, no external deps)."""
import re
import markdown
from fpdf import FPDF

# ── Read Markdown ──
with open('报告.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# ── Convert to HTML ──
html_body = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

# ── PDF class ──
class ReportPDF(FPDF):
    MARGIN = 20  # left/right margin in mm

    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font('YaHei', '', 'C:/Windows/Fonts/msyh.ttc')
        self.add_font('YaHei', 'B', 'C:/Windows/Fonts/msyhbd.ttc')
        self.add_font('Code', '', 'C:/Windows/Fonts/consola.ttf')
        self.set_auto_page_break(True, 20)
        self.set_margin(self.MARGIN)

    def footer(self):
        self.set_y(-15)
        self.set_font('YaHei', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'— {self.page_no()} —', align='C')

    def aw(self):
        """Available width between margins."""
        return self.w - self.l_margin - self.r_margin

    def heading(self, text, level):
        sizes = {1: 22, 2: 17, 3: 13}
        colors = {1: (90, 50, 160), 2: (106, 61, 201), 3: (51, 51, 51)}
        self.ln(4)
        if level <= 2:
            self.set_draw_color(*colors[level])
            self.set_line_width(0.5 if level == 1 else 0.3)
            y = self.get_y()
            self.line(self.l_margin, y, self.l_margin + self.aw(), y)
        self.ln(2)
        self.set_font('YaHei', 'B' if level <= 2 else '', sizes[level])
        self.set_text_color(*colors[level])
        self.multi_cell(0, sizes[level] * 0.45, text)
        self.ln(3 if level == 1 else 2)

    def para(self, text):
        text = text.replace('`', '"')
        # Handle inline <code> tags from codehilite
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'"\1"', text)
        text = re.sub(r'<[^>]+>', '', text)
        self.set_font('YaHei', '', 10)
        self.set_text_color(34, 34, 34)
        self.multi_cell(0, 6.5, text)
        self.ln(1)

    def code_block(self, code_text):
        code_text = (code_text
                     .replace('&lt;', '<').replace('&gt;', '>')
                     .replace('&amp;', '&').replace('&quot;', '"')
                     .replace('&#39;', "'"))
        self.ln(2)
        lines = code_text.split('\n')
        line_h = 5
        pad = 4  # padding in mm
        block_w = self.aw()
        usable_w = block_w - pad * 2

        # Calculate total height
        total_h = pad * 2
        for line in lines:
            if not line.strip():
                total_h += line_h
            else:
                self.set_font('YaHei', '', 8)
                w = self.get_string_width(line)
                rows = max(1, -(-int(w) // int(usable_w)) if w > usable_w else 1)
                total_h += line_h * rows

        # Page break check
        if self.get_y() + total_h > self.h - self.b_margin - 10:
            self.add_page()

        x = self.l_margin
        y = self.get_y()

        # Background
        self.set_fill_color(30, 30, 46)
        self.rect(x, y, block_w, total_h, 'F')

        # Write lines
        cy = y + pad
        for line in lines:
            if cy > self.h - self.b_margin - 10:
                break
            if not line.strip():
                cy += line_h
                continue
            self.set_xy(x + pad, cy)
            self.set_font('YaHei', '', 7.5)
            self.set_text_color(224, 224, 224)
            self.multi_cell(usable_w, line_h, line)
            cy = self.get_y()
        self.set_y(cy + pad - line_h)
        self.ln(2)

    def write_table(self, table_html):
        rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
        if not rows:
            return
        parsed = []
        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            parsed.append([re.sub(r'<[^>]+>', '', c).strip() for c in cells])
        if not parsed:
            return

        ncols = max(len(r) for r in parsed)
        col_w = self.aw() / ncols

        # Header
        self.set_font('YaHei', 'B', 8.5)
        self.set_fill_color(102, 126, 234)
        self.set_text_color(255, 255, 255)
        for cell in parsed[0]:
            self.cell(col_w, 7, cell, border=1, fill=True, align='C')
        self.ln()

        # Data rows
        self.set_font('YaHei', '', 8)
        for idx, row in enumerate(parsed[1:]):
            self.set_fill_color(245, 240, 255) if idx % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_text_color(34, 34, 34)
            row_h = 6
            if self.get_y() + row_h > self.h - self.b_margin - 10:
                self.add_page()
            for cell in row:
                self.cell(col_w, row_h, cell, border=1, fill=True, align='C')
            self.ln()
        self.ln(3)

    def blockquote(self, text):
        text = re.sub(r'<[^>]+>', '', text)
        self.ln(2)
        x, y = self.get_x(), self.get_y()
        self.set_font('YaHei', '', 9.5)
        self.set_text_color(85, 85, 85)
        self.set_x(x + 4)
        self.multi_cell(self.aw() - 8, 6, text)
        new_y = self.get_y()
        self.set_fill_color(124, 77, 255)
        self.rect(x, y, 1.5, new_y - y, 'F')
        self.ln(2)

    def write_list(self, items, ordered=False):
        self.set_font('YaHei', '', 10)
        self.set_text_color(34, 34, 34)
        for idx, item in enumerate(items):
            item = re.sub(r'<[^>]+>', '', item)
            prefix = f'{idx+1}. ' if ordered else '- '
            self.set_x(self.l_margin + 5)
            self.multi_cell(self.aw() - 5, 6.5, prefix + item)
            self.ln(0.5)
        self.ln(1)


# ── Build PDF ──
pdf = ReportPDF()
pdf.add_page()

# Split HTML into top-level blocks
block_pat = r'(<h[1-3]>.*?</h[1-3]>|<pre>.*?</pre>|<table>.*?</table>|<blockquote>.*?</blockquote>|<ul>.*?</ul>|<ol>.*?</ol>|<p>.*?</p>)'
blocks = re.findall(block_pat, html_body, re.DOTALL)

for block in blocks:
    block = block.strip()
    if not block:
        continue

    if block.startswith('<h1>'):
        pdf.heading(re.sub(r'<[^>]+>', '', block), 1)
    elif block.startswith('<h2>'):
        pdf.heading(re.sub(r'<[^>]+>', '', block), 2)
    elif block.startswith('<h3>'):
        pdf.heading(re.sub(r'<[^>]+>', '', block), 3)
    elif block.startswith('<pre>'):
        pdf.code_block(block[5:-6])
    elif block.startswith('<table>'):
        pdf.write_table(block)
    elif block.startswith('<blockquote>'):
        pdf.blockquote(block)
    elif block.startswith('<ul>'):
        pdf.write_list(re.findall(r'<li>(.*?)</li>', block, re.DOTALL))
    elif block.startswith('<ol>'):
        pdf.write_list(re.findall(r'<li>(.*?)</li>', block, re.DOTALL), ordered=True)
    elif block.startswith('<p>'):
        pdf.para(block)

pdf.output('报告.pdf')
print(f'OK → 报告.pdf  ({pdf.pages_count} pages)')
