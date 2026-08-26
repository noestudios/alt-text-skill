# alt-text skill — helper scripts

Two helpers the skill shells out to: one builds the `.docx` deliverable, one rasterizes PDF figures
so they can be described.

## manifest_to_docx.py — build the `.docx` deliverable

Converts an alt-text manifest (Markdown) into the standard-format `.docx` used for layout hand-off.
Cross-platform; requires **python-docx**. One-time bootstrap (a venv keeps system Python clean):

```bash
python3 -m venv .venv
.venv/bin/pip install python-docx      # or: pip install -r ../../requirements.txt
```

Usage:

```bash
# one manifest -> a specific output path (folder-prefixed name lives in the image folder)
.venv/bin/python manifest_to_docx.py "/scratch/Riverside Library.md" \
    --out "/path/Riverside Library/Riverside Library alt-text-manifest.docx" \
    --subtitle "Acme 2025 Sustainability Report"

# batch: every *alt-text-manifest.md under a tree -> a sibling .docx each
.venv/bin/python manifest_to_docx.py "/path/photos" --subtitle "Acme 2025 Sustainability Report"
```

- Title comes from the manifest's `# Alt Text Manifest — <project>` heading.
- `--subtitle` is the report label shown under the title (defaults to a neutral "Image Alt Text").
- Per image it emits Category, Alt text, Long description (complex only), and a Note **only when the
  manifest row has real, non-boilerplate note text**.

## pdf_to_pngs.sh — rasterize PDF figures (cross-platform)

Renders **every page** of a PDF to PNGs. Picks the first backend available:

1. `pdftoppm` (poppler) — best quality, honors the target width
2. `magick` / `convert` (ImageMagick)
3. `osascript pdf_to_pngs.js` (native macOS PDFKit — no extra install)

```bash
bash pdf_to_pngs.sh "<file.pdf>" "<outDir>" 2000
# -> "<outDir>/<pdf-basename> - p01.png", " - p02.png", ...
```

Why a dedicated tool: `sips` and `qlmanage` only rasterize **page 1** of a multi-page PDF.

`pdf_to_pngs.js` is the macOS-only PDFKit fallback invoked by the shell script; you can also call it
directly with `osascript -l JavaScript pdf_to_pngs.js <pdf> <outDir> <widthPx>`.

## Dependencies at a glance

| Need | Tool | Install |
|---|---|---|
| Build `.docx` | python-docx | `pip install python-docx` |
| Rasterize PDF (any OS) | poppler **or** ImageMagick | `brew install poppler` / `apt install poppler-utils` / `brew install imagemagick` |
| Rasterize PDF (macOS, no install) | built-in PDFKit | — |
| Verify `.docx` visually (optional) | LibreOffice **or** macOS QuickLook | `brew install --cask libreoffice` |
