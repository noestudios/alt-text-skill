# alt-text skill

A [Claude](https://claude.com/claude-code) skill that generates **accessible, WCAG-aligned alt text**
for a folder of images and hands it back as a clean **`.docx` per folder** — ready to copy-paste into
InDesign or any layout tool.

Built for real publication workflows (annual reports, brochures, catalogs) where a designer needs
caption-ready alt text next to each image, plus long descriptions for complex figures like charts and
architectural drawings.

## What it does

- **Classifies every image** — decorative, simple informative, functional, complex, or text-as-image —
  and writes alt text to the WCAG rules for each type.
- **Handles PDF figures** (renderings, site plans, floor plans) by rasterizing each page so it can be
  described, referencing it as `Site Plan.pdf — p2`.
- **Treats architectural drawings as complex** — short alt + a long description — and differentiates
  similar sets (four elevations, four perspectives) instead of repeating one description.
- **Grounds descriptions in context** — a source document, a `context.md`, or a client's
  "photo descriptions" `.docx`/`.txt`.
- **Omits personal characteristics by default** — people are described by role and action, never by
  apparent race, gender, or age (configurable).
- **Outputs one standard-format `.docx` per folder**, named with the folder prepended
  (`Riverside Library alt-text-manifest.docx`) so files stay unique when collected.
- **Optional thumbnails** — lay out each entry as *thumbnail | description* (`--thumbs`), with
  downscaled, EXIF-rotated previews (also works for rasterized PDF pages).
- **Optional master index** — one spreadsheet (`.xlsx` or `.csv`) accounting for every image across
  every folder: Folder / # / File / Category / Alt chars / Alt text / Long description / Notes.
- **Flags publication issues** — rotated source files, likely misfiled images, duplicates, mislabeled
  title blocks, and decorative-vs-informative calls for stock imagery.

## Install (drop-in skill)

The skill is the whole `alt-text/` folder — `SKILL.md` **plus** its `scripts/`. Keep them together:
the skill shells out to those scripts to build the `.docx`, so `SKILL.md` on its own won't work.

**Git clone (recommended — brings the scripts):**

```bash
git clone https://github.com/noestudios/alt-text-skill.git
mkdir -p ~/.claude/skills
cp -R alt-text-skill/alt-text ~/.claude/skills/
```

**Claude desktop app:** installing by pointing the app at `SKILL.md` copies **only that file**, not the
`scripts/` folder — the skill will then fail when it tries to run them. After installing, copy `scripts/`
into the same skill directory so it sits next to `SKILL.md` (`…/skills/alt-text/scripts/`), or just use
the git-clone method above, which brings everything.

Then in Claude Code:

```
/alt-text "/path/to/images" "Acme 2025 Annual Report"
```

`images` can be a single folder, or a **parent folder of project subfolders** — each subfolder becomes
its own `.docx`.

## Requirements

| For | Install |
|---|---|
| Building the `.docx` | `pip install python-docx` (see [`requirements.txt`](requirements.txt)) |
| Thumbnails (`--thumbs`) | `pip install Pillow` |
| Master index as `.xlsx` | `pip install openpyxl` (`.csv` needs nothing) |
| Rasterizing PDFs (Linux/Windows) | poppler (`pdftoppm`) **or** ImageMagick (`magick`) |
| Rasterizing PDFs (macOS) | nothing — uses built-in PDFKit |
| Verifying `.docx` visually (optional) | LibreOffice **or** macOS QuickLook |

See [`alt-text/scripts/README.md`](alt-text/scripts/README.md) for the helper-script details.

## How it works

The skill runs a fixed pipeline (full detail in [`alt-text/SKILL.md`](alt-text/SKILL.md)):

1. **Resolve context** — report label, source document / context file, people policy.
2. **Inventory** — list images per folder; rasterize PDF figures; skip source-file duplicates.
3. **Classify & write** — one image at a time, WCAG rules per category.
4. **Working manifest** — a scratch Markdown manifest (crash-safety; not a deliverable).
5. **Verify & flag** — re-check each alt; surface publication issues.
6. **Deliver** — generate the standard-format `.docx` into each folder.

See [`examples/`](examples/) for a sample manifest and the `.docx` it produces.

## Example output

Each image becomes a block like:

> **Image 3.  west-elevation.pdf — p1**
> **Category:** Complex
> **Alt text:** West elevation of Riverside Library, a two-story brick-and-glass building with a
> recessed central entrance and a standing-seam metal roof.
> **Long description:** …
> **Note:** Drawing title block reads "Sheet A2.1"; not confirmed against the sheet index.

## Repository layout

```
alt-text/            ← the drop-in skill (copy this into ~/.claude/skills/)
  SKILL.md
  scripts/
    manifest_common.py    ← shared manifest parser
    manifest_to_docx.py   ← Markdown manifest → standard .docx (optional --thumbs)
    manifest_to_index.py  ← all manifests → one master index (.xlsx/.csv)
    pdf_to_pngs.sh        ← cross-platform PDF page rasterizer
    pdf_to_pngs.js        ← macOS PDFKit fallback
    README.md
examples/            ← sample manifest, generated .docx, and master index .csv
requirements.txt
LICENSE              ← MIT
```

## Contributing

Issues and PRs welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

[MIT](LICENSE) © 2026 Chris Hays
