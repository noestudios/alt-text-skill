# alt-text skill

A [Claude](https://claude.com/claude-code) skill that writes the alt text for a whole folder of images
at once. It opens each image, classifies it, and writes WCAG-aligned alt text grounded in what the
images are actually for, then hands back a `.docx` per folder. Paste that wherever the text needs to
live: website markup, a CMS, an app's strings, an accessibility audit, or a designer's layout.

Any batch of images that needs describing is fair game. It also handles the awkward cases a lot of tools
skip — charts, diagrams, and architectural drawings get a short alt plus a full long description, and
multi-page PDFs are rasterized so their pages can be described too. Publication workflows (annual
reports, brochures, catalogs) were the original use case, but they're just one of many.

## What it does

- Sorts each image into one of five WCAG categories — decorative, simple informative, functional,
  complex, or text-as-image — and writes to the rule for that type. Decorative images get `alt=""`,
  text-in-image gets transcribed, and charts or diagrams get a short alt plus a long description.
- Reads the surrounding context first: a source document, a `context.md`, or the "photo descriptions"
  file a client hands over. The alt text then says what an image is *for*, not just what's in it.
- Doesn't guess at people. By default it describes them by role and action ("a worker installs
  ductwork"), never by apparent race, gender, or age. Flip that off if a project needs it.
- Handles the cases a lot of tools skip. Multi-page PDFs get rasterized page by page (`Site Plan.pdf —
  p2`) so each page can be described; a set of four elevations gets four distinct write-ups, not one
  pasted four times.
- Writes one `.docx` per folder, named after the folder (`Riverside Library alt-text-manifest.docx`) so
  nothing collides when you collect them. Add `--thumbs` and each entry gets a thumbnail next to it.
- Builds a master spreadsheet across every folder by default — one row per image (Folder, #, File,
  Category, Alt chars, Alt text, Long description, Notes). It's a `.csv` unless you ask for `--xlsx`, or
  `--no-index` to skip it.
- Stays quiet while it runs. At the end you get a short note — where the files landed, how many images,
  any errors, how long it took — and the per-image detail lives in the deliverable, not the chat.

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

### Options (flags, anywhere in the command)

```
/alt-text "/path/to/images" "Acme 2025 Annual Report" --thumbs --xlsx
```

| Flag | Effect |
|---|---|
| *(none)* | A `.docx` per folder **plus** an overall `alt-text-index.csv` across all folders. |
| `--thumbs` | Embed a thumbnail beside each entry in the `.docx` (needs Pillow). |
| `--xlsx` | Build the master index as `.xlsx` instead of the default `.csv` (needs openpyxl). |
| `--no-index` | Skip the master index. |
| `--verbose` | Full per-image narration inside each worker (default: a terse `N of <total> images` counter). |

The master index is generated **by default** — no flag needed. Each folder runs in its own parallel
worker, so the images stay out of the main chat; the main flow shows `Writing <folder> manifest`
progress and ends with one short completion note. Pass `--verbose` for full per-image narration inside
the workers. You can also just ask in plain language ("include thumbnails", "skip the index", "be verbose").

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
3. **Classify & write** — each folder in its own parallel worker (images stay out of the main chat),
   one image at a time per worker, WCAG rules per category.
4. **Working manifest** — a scratch Markdown manifest (crash-safety; not a deliverable).
5. **Deliver** — generate the standard-format `.docx` into each folder, plus the master index.
6. **Report** — one short completion note: location, counts, any errors, total time.

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
