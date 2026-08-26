#!/usr/bin/env python3
"""Shared parsing/cleaning for alt-text manifests.

Imported by manifest_to_docx.py (build the .docx deliverable) and
manifest_to_index.py (build the master spreadsheet). Kept dependency-free.
"""
import re

# Notes boilerplate that is manifest-internal navigation, not a real per-image note.
BOILERPLATE_PATTERNS = [
    r'\(short alt \+ long description below\)\.?',
    r'short alt \+ long description below\.?',
    r'see long description( below)?\.?',
    r'long description below\.?',
]

def clean_note(note):
    """Strip navigation boilerplate; return '' when no real note remains."""
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
    """Normalize a category cell to one canonical label."""
    cl = c.lower()
    if cl.startswith('decorative'): return 'Decorative'
    if 'text-as-image' in cl or 'text as image' in cl: return 'Text-as-image'
    if cl.startswith('functional'): return 'Functional'
    if cl.startswith('complex'): return 'Complex'
    if 'simple' in cl: return 'Simple informative'
    return c.strip()

def norm_key(s):
    """Normalize a filename / long-desc heading for fuzzy matching."""
    s = s.strip()
    s = re.sub(r'^image\s+\d+\s*[—–-]\s*', '', s, flags=re.I)   # drop "Image N —" prefix
    s = re.split(r'\s{2,}\(', s)[0]                              # cut trailing "  (descriptor)"
    return re.sub(r'\s+', ' ', s).strip().lower()

def project_name(title):
    """'Alt Text Manifest — Foo' -> 'Foo'."""
    return re.sub(r'^Alt Text Manifest\s*[—–-]\s*', '', title or '').strip() or 'Alt Text'

def parse_manifest(path):
    """Return {title, generated, people, rows[], longs{normkey: [paras]}}."""
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


# --- image resolution (used by --thumbs) --------------------------------------
_PDF_PAGE_RE = re.compile(r'^(?P<base>.+\.pdf)\s*[—–-]\s*p?(?P<page>\d+)\s*$', re.IGNORECASE)

def resolve_image_path(file_cell, images_dir, raster_dir=None):
    """Best-effort map a manifest File cell to an actual image path.

    Regular files resolve under images_dir. A PDF-page reference like
    'Site Plan.pdf — p2' resolves to a rasterized '<base> - pNN.png' under
    raster_dir (default images_dir). Returns a path or None.
    """
    import os, glob
    raster_dir = raster_dir or images_dir
    direct = os.path.join(images_dir, file_cell)
    if os.path.isfile(direct):
        return direct
    m = _PDF_PAGE_RE.match(file_cell)
    if m:
        base = os.path.splitext(os.path.basename(m.group('base')))[0]
        page = int(m.group('page'))
        for pat in (f"{base} - p{page:02d}.png", f"{base} - p{page}.png",
                    f"{base}-{page:02d}.png", f"{base}-{page}.png"):
            cand = os.path.join(raster_dir, pat)
            if os.path.isfile(cand):
                return cand
        # last resort: any file that startswith base and ends with the page number
        for cand in glob.glob(os.path.join(raster_dir, f"{glob.escape(base)}*.png")):
            if re.search(rf'[-p]0*{page}\.png$', os.path.basename(cand)):
                return cand
    return None
