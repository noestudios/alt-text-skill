#!/usr/bin/env python3
"""Convert alt-text manifest Markdown into a standard-format .docx for layout hand-off.

Usage:
    python manifest_to_docx.py <manifest.md> [--out <path.docx>] [--subtitle "<text>"]
    python manifest_to_docx.py <dir> [--subtitle "<text>"]      # recurse: every *alt-text-manifest.md

Per image the .docx shows: Category, Alt text, Long description (complex only), and a Note
ONLY when one is present. Title = project name from the manifest heading; subtitle = --subtitle.

Requires python-docx  (pip install python-docx). See README.md for the venv bootstrap.
"""
import os, re, sys, glob, argparse
try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
except ImportError:
    sys.exit("python-docx is required: python3 -m venv .venv && .venv/bin/pip install python-docx")
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DEFAULT_SUBTITLE = "Image Alt Text"

# Notes boilerplate that is manifest-internal navigation, not a real per-image note.
BOILERPLATE_PATTERNS = [
    r'\(short alt \+ long description below\)\.?',
    r'short alt \+ long description below\.?',
    r'see long description( below)?\.?',
    r'long description below\.?',
]

def clean_note(note):
    if note is None:
        return ""
    n = note.strip()
    if n.lower() in ("", "—", "-", "–", "n/a", "none"):
        return ""
    for pat in BOILERPLATE_PATTERNS:
        n = re.sub(pat, "", n, flags=re.IGNORECASE)
    n = re.sub(r'\s+', ' ', n).strip().strip(" .;,").strip()
    n = re.sub(r'\.\s*\.', '.', n)
    n = re.sub(r'"\s*\.\s*$', '."', n)
    if n and not n.endswith((".", "!", "?", '"')):
        n += "."
    return n

def norm_cat(c):
    cl = c.lower()
    if cl.startswith('decorative'): return 'Decorative'
    if 'text-as-image' in cl or 'text as image' in cl: return 'Text-as-image'
    if cl.startswith('functional'): return 'Functional'
    if cl.startswith('complex'): return 'Complex'
    if 'simple' in cl: return 'Simple informative'
    return c.strip()

def norm_key(s):
    s = s.strip()
    s = re.sub(r'^image\s+\d+\s*[—–-]\s*', '', s, flags=re.I)   # drop "Image N —" prefix
    s = re.split(r'\s{2,}\(', s)[0]                              # cut trailing "  (descriptor)"
    return re.sub(r'\s+', ' ', s).strip().lower()

def parse_manifest(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    title = generated = people = ""
    for ln in lines[:8]:
        if ln.startswith("# ") and not title:
            title = ln[2:].strip()
        elif ln.lower().startswith("generated:"):
            generated = ln.split(":", 1)[1].strip()
        elif ln.lower().startswith("people policy:"):
            people = ln.split(":", 1)[1].strip()
    rows = []
    for ln in lines:
        if re.match(r'^\|\s*\d+\s*\|', ln):
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            while len(cells) < 5:
                cells.append("")
            rows.append({"idx": cells[0], "file": cells[1], "category": cells[2],
                         "alt": cells[3], "notes_raw": cells[4]})
    longs = {}
    if "## Long descriptions" in text:
        block = text.split("## Long descriptions", 1)[1]
        for p in re.split(r'\n###\s+', block)[1:]:
            seg = p.splitlines()
            key = seg[0].strip()
            body = "\n".join(seg[1:]).strip()
            paras = [para.strip() for para in re.split(r'\n\s*\n', body) if para.strip()]
            longs[norm_key(key)] = paras
    return {"title": title, "generated": generated, "people": people, "rows": rows, "longs": longs}

# ---- docx helpers ----
def add_hr(paragraph, color="888888", sz="8"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr'); bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), sz)
    bottom.set(qn('w:space'), '2'); bottom.set(qn('w:color'), color)
    pBdr.append(bottom); pPr.append(pBdr)

def field(doc, label, value, label_color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(0)
    r = p.add_run(label); r.bold = True
    if label_color:
        r.font.color.rgb = label_color
    p.add_run(" "); p.add_run(value)
    return p

def build_doc(model, out_path, subtitle):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5); sec.page_height = Inches(11)
    for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, m, Inches(1))
    normal = doc.styles['Normal']; normal.font.name = 'Calibri'; normal.font.size = Pt(11)
    style_names = [s.name for s in doc.styles]
    grey = RGBColor(0x60, 0x60, 0x60)

    project = re.sub(r'^Alt Text Manifest\s*[—–-]\s*', '', model['title']).strip() or "Alt Text"
    doc.add_heading(project, level=0)
    if subtitle:
        sp = doc.add_paragraph(subtitle)
        if 'Subtitle' in style_names:
            sp.style = doc.styles['Subtitle']
    def meta(text):
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = grey
        return p
    if model['people']:
        meta(f"People policy: {model['people']}")
    if model['generated']:
        meta(f"Generated: {model['generated']}")
    legend = meta("For each image below: Category, Alt text, Long description (complex figures only), "
                  "and a Note where one applies. Alt text is the caption-ready text for InDesign.")
    add_hr(legend); legend.paragraph_format.space_after = Pt(8)

    used = set()
    for row in model['rows']:
        cat = norm_cat(row['category']); alt = row['alt'].strip()
        note = clean_note(row['notes_raw'])
        long_paras = model['longs'].get(norm_key(row['file']))
        if long_paras is not None:
            used.add(norm_key(row['file']))
        head = doc.add_heading(f"Image {row['idx']}.  {row['file']}", level=2)
        head.paragraph_format.space_before = Pt(10); head.paragraph_format.space_after = Pt(3)
        field(doc, "Category:", cat)
        # decorative images intentionally have empty alt — show it explicitly so it doesn't read as missing
        field(doc, "Alt text:", alt if alt else ('""' if cat == 'Decorative' else alt))
        if long_paras:
            lp = doc.add_paragraph(); lp.paragraph_format.space_after = Pt(2)
            lp.add_run("Long description:").bold = True
            for para in long_paras:
                dp = doc.add_paragraph(para)
                dp.paragraph_format.left_indent = Inches(0.25); dp.paragraph_format.space_after = Pt(4)
        if note:
            field(doc, "Note:", note, label_color=RGBColor(0x99, 0x5A, 0x00))

    orphan = [(k, v) for k, v in model['longs'].items() if k not in used]
    if orphan:
        doc.add_heading("Additional long descriptions", level=2)
        for k, paras in orphan:
            doc.add_paragraph(k).runs[0].bold = True
            for para in paras:
                doc.add_paragraph(para)

    doc.save(out_path)
    return len(model['rows']), len(orphan)

def iter_manifests(paths):
    for p in paths:
        if os.path.isdir(p):
            for m in sorted(set(glob.glob(os.path.join(p, "**", "*alt-text-manifest.md"), recursive=True)
                                + glob.glob(os.path.join(p, "*alt-text-manifest.md")))):
                yield m, None
        else:
            yield p, None

def main():
    ap = argparse.ArgumentParser(description="Convert alt-text manifest .md to a standard .docx.")
    ap.add_argument("paths", nargs="+", help="manifest .md file(s) or dir(s) to recurse")
    ap.add_argument("--out", help="output .docx path (only valid with a single manifest file)")
    ap.add_argument("--subtitle", default=DEFAULT_SUBTITLE, help="report label shown under the title")
    args = ap.parse_args()

    items = list(iter_manifests(args.paths))
    if args.out and len(items) != 1:
        sys.exit("--out is only valid when exactly one manifest is given")
    total = 0
    for md, _ in items:
        model = parse_manifest(md)
        out = args.out if args.out else (md[:-3] + ".docx")
        rows, orphan = build_doc(model, out, args.subtitle)
        flag = f"  [!! {orphan} orphan long-desc]" if orphan else ""
        print(f"OK  rows={rows:2d}{flag}  ->  {out}")
        total += 1
    print(f"\nGenerated {total} .docx file(s).")

if __name__ == "__main__":
    main()
