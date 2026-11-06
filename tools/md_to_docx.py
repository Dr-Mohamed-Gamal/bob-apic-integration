#!/usr/bin/env python3
"""Convert the filled SRS from Markdown to Word, in the bank's template: python3 tools/md_to_docx.py <file.md> [<out.docx>]

Bob writes the SRS in Markdown from templates/API-SRS-API_Connect_TEMPLATE.md. This script builds the
.docx on top of templates/API-SRS-API_Connect_TEMPLATE.docx: it keeps the template's header, footer,
styles, page setup, cover page, page breaks, heading styles, table colours and column widths, and
replaces only the body text with the filled document.
Pure Python standard library: works on Windows, macOS and Linux with no extra packages.
"""
import html
import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "API-SRS-API_Connect_TEMPLATE.docx")
FONT = '<w:rFonts w:ascii="Verdana" w:hAnsi="Verdana" w:eastAsia="Verdana"/>'
MONO = '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="Consolas"/>'
WIDTH = 9071                      # usable width of the template's tables, in twentieths of a point
HEADER_FILL = "BFBFBF"            # grey header row
LABEL_FILL = "D9D9D9"             # requirement table labels
TITLE_FILL = "8DB3E2"             # "Input Headers" title row
PAGE_BREAK_BEFORE = ("APPROVAL SIGNATURES", "REVISION RECORD", "TABLE OF CONTENTS")


def run(text, bold=False, italic=False, mono=False, size=None):
    p = (MONO if mono else FONT) + ("<w:b/>" if bold else '<w:b w:val="0"/>')
    p += "<w:i/>" if italic else ""
    p += f'<w:sz w:val="{size}"/>' if size else ""
    return f'<w:r><w:rPr>{p}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def runs(text, bold=False, size=None):
    """Inline Markdown (**bold**, *italic*, `code`) to Word runs."""
    text = html.unescape(text)
    out = []
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|(?<![*\w])\*[^*]+\*(?!\w))", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            out.append(run(part[2:-2], True, size=size))
        elif part.startswith("`") and part.endswith("`"):
            out.append(run(part[1:-1], bold, mono=True, size=size))
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            out.append(run(part[1:-1], bold, True, size=size))
        else:
            out.append(run(part, bold, size=size))
    return "".join(out)


def para(content, style=None, jc=None, ind=None, after=None, before=None, page_break=False):
    ppr = f'<w:pStyle w:val="{style}"/>' if style else ""
    if after is not None or before is not None:
        ppr += "<w:spacing" + (f' w:before="{before}"' if before is not None else "") + \
               (f' w:after="{after}"' if after is not None else "") + "/>"
    ppr += f'<w:ind w:left="{ind}"/>' if ind is not None else ""
    ppr += f'<w:jc w:val="{jc}"/>' if jc else ""
    br = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>' if page_break else ""
    return f"{br}<w:p><w:pPr>{ppr}</w:pPr>{content}</w:p>"


def cell(content_runs, width, fill=None, span=1):
    tcpr = f'<w:tcW w:type="dxa" w:w="{width}"/>'
    tcpr += f'<w:gridSpan w:val="{span}"/>' if span > 1 else ""
    tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
    return f'<w:tc><w:tcPr>{tcpr}</w:tcPr><w:p><w:pPr><w:spacing w:before="20" w:after="20"/></w:pPr>{content_runs}</w:p></w:tc>'


def table(rows, widths, grid=True, header=True, title=None, size=17):
    """rows: list of lists of cell text. A row with text only in its first cell is a merged sub-heading."""
    n = len(widths)
    tblpr = ('<w:tblStyle w:val="TableGrid"/>' if grid else "") + '<w:tblW w:type="auto" w:w="0"/>'
    tblpr += '<w:jc w:val="center"/>' if grid else ""
    tblpr += '<w:tblLayout w:type="fixed"/><w:tblLook w:firstColumn="1" w:firstRow="1" w:lastColumn="0" w:lastRow="0" w:noHBand="0" w:noVBand="1" w:val="04A0"/>'
    out = [f"<w:tbl><w:tblPr>{tblpr}</w:tblPr><w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"]
    if title:
        out.append("<w:tr>" + cell(runs(title, True, size), sum(widths), TITLE_FILL, n) + "</w:tr>")
    for i, r in enumerate(rows):
        r = (r + [""] * n)[:n]
        is_head = header and i == 0
        if not is_head and n > 1 and r[0].strip() and not any(c.strip() for c in r[1:]) and r[0].strip().startswith("**"):
            out.append("<w:tr>" + cell(runs(r[0], True, size), sum(widths), None, n) + "</w:tr>")
            continue
        out.append("<w:tr>" + "".join(
            cell(runs(c, is_head, size), widths[j], HEADER_FILL if is_head else None) for j, c in enumerate(r)) + "</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def template_widths(doc_xml):
    """Column widths of the template's tables, keyed by their header texts."""
    known = {}
    for tb in re.findall(r"<w:tbl>.*?</w:tbl>", doc_xml, re.S):
        grid = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"', tb)]
        for tr in re.findall(r"<w:tr[ >].*?</w:tr>", tb, re.S):
            cells = ["".join(re.findall(r"<w:t[^>]*>([^<]*)", c)).strip() for c in re.findall(r"<w:tc>.*?</w:tc>", tr, re.S)]
            if len(cells) == len(grid):
                known[tuple(html.unescape(c).lower() for c in cells)] = grid
                break
    return known


def widths_for(head, known):
    key = tuple(re.sub(r"\*", "", h).strip().lower() for h in head)
    if key in known:
        return known[key]
    n = len(head)
    return [WIDTH // n] * n


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md, doc_xml):
    known = template_widths(doc_xml)
    lines = md.split("\n")
    body, i, cover, toc, pending_title = [], 0, True, False, None
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("# "):                                          # cover title
            body += ["<w:p/>"] * 5 + [para(run(s[2:], True, size=40), jc="right")]
            i += 1
            continue
        if cover and re.fullmatch(r"\*\*[^*]+\*\*", s) and s[2:-2] not in PAGE_BREAK_BEFORE:   # project name on the cover
            body.append(para(run(html.unescape(s[2:-2]), size=26), jc="right"))
            i += 1
            continue
        if cover and s.startswith("- ") and ":" in s:                    # cover details: borderless 2-column table
            rows = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                k, _, v = lines[i].strip()[2:].partition(":")
                rows.append([k.strip() + " :", v.strip()])
                i += 1
            body += ["<w:p/>", table(rows, [2551, 6520], grid=False, header=False, size=19)]
            continue
        m = re.fullmatch(r"\*\*([A-Z][A-Z ]+)\*\*", s)                   # front-matter titles
        if m:
            cover = False
            toc = m.group(1) == "TABLE OF CONTENTS"
            body.append(para(run(m.group(1), True, size=24), jc="center", page_break=m.group(1) in PAGE_BREAK_BEFORE))
            i += 1
            continue
        if s.startswith("#"):
            level = len(s) - len(s.lstrip("#"))
            text = s[level:].strip()
            first_h1 = level == 2 and toc
            toc = False
            body.append(para(f'<w:r><w:t xml:space="preserve">{escape(html.unescape(text))}</w:t></w:r>',
                             style=f"Heading{min(level - 1, 3)}", page_break=first_h1))
            i += 1
            continue
        if toc and s.startswith("- "):                                   # table of contents entries
            depth = (len(line) - len(line.lstrip())) // 2
            body.append(para(run(html.unescape(s[2:]), bold=depth == 0), ind=340 * depth, after=20))
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not re.fullmatch(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?", lines[i].strip()):
                    rows.append(split_row(lines[i]))
                i += 1
            body.append(table(rows, widths_for(rows[0], known), title=pending_title))
            pending_title = None
            continue
        if s.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(para(run(lines[i].rstrip(), mono=True, size=17), after=0, before=0))
                i += 1
            i += 1
            continue
        if s.startswith("- **Requirement Serial No.**") or s.startswith("- **Unique Req. Ref. No.**"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("- **"):
                parts = [p.strip() for p in lines[i].strip()[2:].split("·")]
                row = []
                for p in parts:
                    mm = re.match(r"\*\*(.+?)\*\*\s*(.*)", p)
                    row += [mm.group(1), mm.group(2)] if mm else [p, ""]
                rows.append(row)
                i += 1
            w = [2041, 2041, 1247, 3742]
            xml = [f'<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:type="auto" w:w="0"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>' + "".join(f'<w:gridCol w:w="{x}"/>' for x in w) + "</w:tblGrid>"]
            for r in rows:
                r = (r + [""] * 4)[:4]
                xml.append("<w:tr>" + "".join(cell(runs(c, j % 2 == 0, 17), w[j], LABEL_FILL if j % 2 == 0 else None) for j, c in enumerate(r)) + "</w:tr>")
            body += ["".join(xml) + "</w:tbl>", "<w:p/>"]
            continue
        if s.startswith("- ") or s.startswith("* "):
            body.append(para(runs(s[2:]), style="ListBullet"))
            i += 1
            continue
        if s == "**Input Headers**":                                     # becomes the table's blue title row
            pending_title = "Input Headers"
            i += 1
            continue
        if s.startswith(">"):
            body.append(para(runs(s.lstrip("> ")), ind=340))
            i += 1
            continue
        body.append(para(runs(s)))
        i += 1
    return "".join(body)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".docx"
    with open(src, encoding="utf-8") as f:
        md = f.read()
    with zipfile.ZipFile(TEMPLATE) as t:
        doc = t.read("word/document.xml").decode("utf-8")
        head = doc[: doc.index("<w:body>") + len("<w:body>")]
        sect = re.findall(r"<w:sectPr.*?</w:sectPr>", doc, re.S)[-1]
        new_doc = head + convert(md, doc) + sect + "</w:body></w:document>"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for item in t.infolist():
                name = item.filename
                if name == "docProps/thumbnail.jpeg":                     # the template's preview picture
                    continue
                data = t.read(name)
                if name == "word/document.xml":
                    data = new_doc.encode("utf-8")
                elif name == "_rels/.rels":
                    data = re.sub(rb'<Relationship [^>]*thumbnail[^>]*/>', b"", data)
                z.writestr(item, data)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
