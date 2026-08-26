# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.1] — 2026-08-26

### Changed
- Added a **"Required inputs"** preflight to `SKILL.md`: when invoked without an images directory or
  report label, the skill now asks for them plainly (in one message) instead of assuming or proceeding
  context-blind.

## [0.2.0] — 2026-08-26

### Added
- **Master index spreadsheet** — `scripts/manifest_to_index.py` aggregates every manifest under a
  tree into one row-per-image `.xlsx` (frozen header + autofilter, via openpyxl) or `.csv`
  (dependency-free). Columns: Folder / # / File / Category / Alt chars / Alt text / Long description /
  Notes.
- **Thumbnails** — `manifest_to_docx.py --thumbs` lays out each entry as *thumbnail | description*,
  with downscaled, EXIF-rotated previews (Pillow). Resolves both plain image files and `X.pdf — pN`
  rasterized pages (`--images-dir` / `--raster-dir` / `--thumb-width`).
- `scripts/manifest_common.py` — shared manifest parser used by both generators.
- Example master index (`examples/sample-index.csv`).

### Changed
- Refactored the manifest parser out of `manifest_to_docx.py` into `manifest_common.py`.

## [0.1.0] — 2026-08-26

Initial open-source release.

### Added
- `alt-text` skill (`SKILL.md`) — six-step pipeline: resolve context, inventory, classify & write,
  working manifest, verify & flag, deliver.
- Per-folder **`.docx` deliverable** with a standard per-image format (Category, Alt text, Long
  description for complex figures, Note only when present), named with the folder prepended.
- `scripts/manifest_to_docx.py` — Markdown manifest → standard `.docx` (python-docx), with fuzzy
  long-description matching and note-boilerplate stripping.
- `scripts/pdf_to_pngs.sh` — cross-platform PDF page rasterizer (poppler → ImageMagick → macOS
  PDFKit fallback).
- `scripts/pdf_to_pngs.js` — native macOS PDFKit rasterizer (multi-page).
- People policy defaults to **omit**; report label is parameterized.
- Example manifest and generated `.docx`.
