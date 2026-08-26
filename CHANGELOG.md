# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

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
