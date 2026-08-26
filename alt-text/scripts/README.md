# alt-text skill — helper scripts

Small tools the skill shells out to. `manifest_common.py` holds the shared manifest parser used by
the two generators.

## manifest_to_docx.py — build the `.docx` deliverable

Converts an alt-text manifest (Markdown) into the standard-format `.docx` used for layout hand-off.
Cross-platform; requires **python-docx**. One-time bootstrap (a venv keeps system Python clean):

```bash
python3 -m venv .venv
.venv/bin/pip install python-docx            # or: pip install -r ../../requirements.txt
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

### `--thumbs` — a thumbnail beside each description (needs Pillow)

```bash
.venv/bin/pip install Pillow
.venv/bin/python manifest_to_docx.py "/scratch/White Flint.md" \
    --out "/path/White Flint/White Flint alt-text-manifest.docx" --subtitle "Acme 2025 Report" \
    --thumbs --images-dir "/path/White Flint" --raster-dir "/scratch/white-flint-pdf-pages"
```

Each entry becomes a *thumbnail | description* row. Thumbnails are downscaled and EXIF-rotated.
`--images-dir` defaults to the manifest's own folder; `--raster-dir` (for `X.pdf — pN` rows) defaults
to `--images-dir`. `--thumb-width` sets the width in inches (default 1.6). Rows whose image can't be
found are reported and fall back to text-only.

## manifest_to_index.py — master index spreadsheet (all folders)

Aggregates every `*alt-text-manifest.md` under a tree into one spreadsheet, one row per image:
Folder / # / File / Category / Alt chars / Alt text / Long description / Notes.

```bash
# .xlsx (frozen header + autofilter) — needs openpyxl
.venv/bin/pip install openpyxl
.venv/bin/python manifest_to_index.py "/path/photos" --out "/path/photos/alt-text-index.xlsx"

# .csv — no dependencies
.venv/bin/python manifest_to_index.py "/path/photos" --out "/path/photos/alt-text-index.csv"
```

With no `--out`, it writes `alt-text-index.xlsx` when openpyxl is present, otherwise `.csv`.

## pdf_to_pngs.sh — rasterize PDF figures (cross-platform)

Renders **every page** of a PDF to PNGs, picking the first backend available: `pdftoppm` (poppler) →
`magick`/`convert` (ImageMagick) → `pdf_to_pngs.js` (native macOS PDFKit; no install).

```bash
bash pdf_to_pngs.sh "<file.pdf>" "<outDir>" 2000
# -> "<outDir>/<pdf-basename> - p01.png", " - p02.png", ...
```

Why a dedicated tool: `sips` and `qlmanage` only rasterize **page 1** of a multi-page PDF.

## Dependencies at a glance

| Need | Tool | Install |
|---|---|---|
| Build `.docx` | python-docx | `pip install python-docx` |
| Thumbnails (`--thumbs`) | Pillow | `pip install Pillow` |
| Master index `.xlsx` | openpyxl | `pip install openpyxl` |
| Master index `.csv` | — (stdlib) | — |
| Rasterize PDF (Linux/Win) | poppler **or** ImageMagick | `apt install poppler-utils` / `brew install imagemagick` |
| Rasterize PDF (macOS) | built-in PDFKit | — |
| Verify `.docx` visually | LibreOffice **or** macOS QuickLook | `brew install --cask libreoffice` |
