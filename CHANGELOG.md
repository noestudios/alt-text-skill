# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.4.0] — 2026-08-26

### Added
- `--verbose` flag — full per-image narration (file, category, alt text) during a run.

### Changed
- **Default run output is now a simple, minimal progress meter** instead of narrating every image:
  `N of <total> images` per image, `Writing <folder> manifest` per folder, and `Writing <project>
  manifest` for the master index. Full per-image detail still lands in the Step 5 report; `--verbose`
  restores the old narration.
- **No per-run self-testing of the tooling** — the helper scripts are deterministic and tested, so the
  skill trusts their `OK …` output instead of reading the parser to confirm the manifest format or
  re-opening/rendering/introspecting the `.docx` to re-verify a build. It investigates only when a
  script flags a warning (orphaned long-description, missing thumbnail). The image-quality re-view in
  Step 5 is unchanged.

## [0.3.0] — 2026-08-26

### Added
- **Command flags** recognized anywhere in the `/alt-text` invocation, documented in the argument hint
  and a new "Command options" section: `--thumbs` (embed thumbnails), `--xlsx` (master index as
  `.xlsx`), `--no-index` (skip the master index). Flags are parsed out before the positional args, so a
  `--flag` is never mistaken for the document path.
- The skill now **proactively offers** the finishing options (thumbnails, and an `.xlsx` upgrade for the
  index) in its end-of-run report, instead of leaving them undiscoverable.

### Changed
- **The master index is now produced by default** — every run writes one overall `alt-text-index.csv`
  across all folders unless `--no-index` is given (previously opt-in only).
- Scratch manifests are named `<folder> alt-text-manifest.md` in one shared scratch dir so the default
  index reliably finds every folder's manifest.

## [0.2.2] — 2026-08-26

### Fixed
- **README install instructions**: replaced the `<you>` placeholder in the clone URL with the real repo
  owner (`noestudios`); added `mkdir -p ~/.claude/skills` so `cp` lands the skill at
  `.../skills/alt-text/` on a fresh machine instead of misplacing it; and documented that installing via
  the Claude desktop app (selecting `SKILL.md`) copies **only that file** — the `scripts/` folder must
  accompany it or the skill fails when it shells out to build the `.docx`.

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
