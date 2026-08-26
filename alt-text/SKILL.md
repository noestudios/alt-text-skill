---
name: alt-text
description: Generate accessible alt text for a directory of images (or a parent folder of project subfolders), for inclusion in a document. Classifies each image (decorative, informative, functional, complex, text-as-image), applies WCAG-aligned writing rules, rasterizes PDF/rendering figures so they can be described, and outputs a standard-format .docx per folder for layout hand-off — plus a master index spreadsheet across all folders by default, and optional thumbnails beside each entry. Use when the user asks for alt text, image descriptions, or accessibility text for images.
argument-hint: [images-dir] [report-label] [document-path] [--thumbs] [--xlsx] [--no-index] [--verbose]
arguments: [images_dir, report_label, document]
disable-model-invocation: true
allowed-tools: Read Glob Grep Bash Write
---

# Alt Text Generator

Generate accessible alt text for every image in `$images_dir`, grounded in document context, and
deliver the results as a standard-format **`.docx`** per folder that a designer copy-pastes into
InDesign (or similar). The Markdown manifest is an internal working file only — see Step 4.

Bundled helpers live in `scripts/` (see `scripts/README.md`): `manifest_to_docx.py` builds the
`.docx`; `pdf_to_pngs.sh` rasterizes PDF pages so they can be viewed and described. These helpers are
deterministic and already tested — **trust them.** Rely on the `OK …` line each prints (and any warning
it flags); don't read their source to confirm behavior, and don't re-open, render, or introspect their
output to re-verify it on a normal run.

## Required inputs — confirm before doing anything

Do not start until you have these. If any **required** one wasn't provided when the skill was
invoked, ask the user for them in ONE brief, plain message (all at once — do not interrogate one at a
time), then proceed. Never guess a directory or invent a report name.

- **`images_dir`** *(required)* — the folder of images to describe, or a parent folder whose
  subfolders are separate projects. No directory means there is nothing to do: ask for the path.
- **`report_label`** *(required)* — the report/publication name; it becomes the `.docx` subtitle
  (e.g., "Acme 2025 Annual Report").
- **`document`** *(optional)* — a source document to ground the descriptions in.

Example plain ask when invoked bare: *"To generate alt text I need two things: (1) the folder of
images (or a parent folder of project subfolders), and (2) the report name to put on the documents.
Optionally, point me at a source document for context. What are they?"*

## Command options (flags)

Beyond the positional inputs, the invocation may carry flags — anywhere in the command, e.g.
`/alt-text "<images>" "<report label>" --thumbs --xlsx`. Recognize them from the argument string, and
honor the equivalent plain-language request the same way ("include thumbnails", "make the index xlsx",
"skip the index"). A `--flag` token is **never** a positional value: strip flags out first, then the
remaining positionals are images-dir, report-label, document (so `--thumbs` is never mistaken for the
document path).

- `--thumbs` — embed a thumbnail beside each entry in every `.docx` (needs Pillow). Default: off (text-only).
- `--xlsx` — build the master index as `.xlsx` instead of the default `.csv` (needs openpyxl).
- `--no-index` — skip the master index for this run.
- `--verbose` — narrate every image as it's processed (file, category, the alt text written). Default:
  off — show the concise progress meter instead (`N of <total> images`; `Writing <name> manifest`). See Step 3.

**The master index is ON by default.** Unless `--no-index` is given, every run finishes by producing one
overall index across all folders (Step 6) — `.csv` by default, `.xlsx` with `--xlsx`.

## Step 1: Resolve context (required before generating anything)

Never generate alt text without at least a document purpose. Resolve:

1. **Report label** (`$report_label`): confirmed above (Required inputs); it becomes the `.docx`
   subtitle.
2. **Document** (`$document` non-empty): read it. Map each image to where it appears; the surrounding
   prose is the primary context — it determines whether an image is redundant, decorative, or carrying
   information the text doesn't.
3. **Context / description file**: if no document, look inside `$images_dir` for a context or caption
   file — `context.md`/`context.txt`, **or a "photo descriptions" `*.docx`/`*.txt`** a client often
   supplies (extract `.docx` text with `pandoc -t plain file.docx`, or macOS `textutil -convert txt
   -stdout file.docx`). Expected shape: purpose/audience at the top, then optional per-image entries
   (`filename: note`). Per-image entries act as overrides (force decorative, supply a proper noun, mark
   functional/linked).
4. Otherwise proceed on the report label alone (it tells you what each building/project/subject is).

**People policy — default: `omit`.** Describe people only by role/action (e.g., "a worker installs
ductwork," "officials cut a ceremonial ribbon"), never their apparent race, gender, age, or physical
characteristics, and never guess a name. Deviate only if the user says so or a context file carries a
`people: describe` line.

## Step 2: Inventory (and folder mode)

- **One worker per folder (default).** Each folder that holds images is its own deliverable (its own
  `.docx`): every subfolder of a parent is one, and loose images sitting directly in the parent form one
  more. **Process each in its own subagent worker, in parallel.** The worker opens and views that
  folder's images in its own context — so the image rendering stays out of the main conversation, and
  the folders run concurrently rather than one image at a time (faster). This is the default even for a
  single folder. The main thread coordinates the workers, shows per-folder progress (Step 3), and
  afterward builds the `.docx` deliverables and the master index from the shared scratch manifests.
- List image files (png, jpg, jpeg, gif, webp, svg) per folder. Report the count. If a single folder
  has more than 40, confirm before proceeding.
- **PDF figures** (architectural renderings, site plans, floor plans) are in scope as report figures.
  Rasterize every page to PNG into a scratch dir and describe each page:
  `bash scripts/pdf_to_pngs.sh "<file.pdf>" "<scratchDir>" 2000`
  Reference each in the manifest by source + page, e.g. `Site Plan.pdf — p2`.
- **Skip non-web source duplicates** (`.tif`, `.psd`, `.ai`) when they mirror an existing raster
  (same basename as a `.png`/`.jpg`) — don't describe them; note them once as the source file.

## Step 3: Classify, then write — one image at a time

Process images individually. Do not batch multiple images into one Read — quality drops. View, then:

**Progress output — simple and minimal.** View **one image per Read** (quality, not chatter), but do
**not** narrate each image. Because each folder runs in its own worker (Step 2), the meter splits
cleanly:

- **Inside each worker** (its own panel, out of the main chat): a terse counter per image —
  `N of <total> images` (`1 of 23 images`, `2 of 23 images`, …), `<total>` being that folder's image
  count. With **`--verbose`** the worker narrates each image (file, category, alt text) instead of the
  bare counter.
- **In the main thread:** `Writing <folder> manifest` as each folder's `.docx` is built, and
  `Writing <project> manifest` when the master index is built. Nothing per image.

The real detail lands once, in the Step 5 report.

**Classify first** into exactly one category:

| Category | Rule |
|---|---|
| Decorative | Adds no information beyond adjacent text/ambience → `alt=""` with a one-line justification in the notes column |
| Simple informative | Conveys information → concise alt, ~125 characters target |
| Functional | Acts as a link or control → alt describes the destination/action, not the appearance |
| Complex | Charts, diagrams, infographics, screenshots, **and architectural drawings** (elevations, sections, site plans, floor plans, renderings) with meaningful detail → short alt PLUS a long description |
| Text-as-image | Text is the content → transcribe verbatim as the alt |

**Writing rules (hard constraints):**

- Never open with "image of," "picture of," "photo of," "rendering of," "graphic showing," or equivalents.
- ~125 character target for simple alt. Content-driven — end at a complete thought, never truncate mid-idea.
- Charts and data visuals: convey the takeaway and key figures, not the visual encoding.
- **Architectural drawings are Complex:** short alt (what it is + headline — which facade/view,
  building form, materials) plus a long description (stories, materials, glazing pattern, roofline,
  entrances, labeled dimensions/roads/rooms, orientation). When several similar drawings appear
  (e.g., four elevations, four perspectives), **differentiate each by facade/vantage — never
  copy-paste** a shared description.
- Do not editorialize or attribute emotion, intent, or mood not visually present.
- Proper nouns only when confidently identifiable; else describe generically and flag in the notes
  column — never guess a name.
- Do not duplicate information the surrounding document text already states.
- Apply the people policy consistently across all images.

## Step 4: Working manifest (internal — NOT the deliverable)

Write results incrementally to a Markdown manifest **in a scratch/temp directory, not the image
folder** — this is crash-safety for a long run, and it feeds the `.docx` generator. The image folder
receives only the `.docx` (Step 6). Name each scratch manifest `<folder> alt-text-manifest.md` and keep
them all in one shared scratch dir, so the default master index (Step 6) finds every folder's manifest.

Manifest format — this is authoritative; the generators parse exactly this shape, so there's no need to
read the parser to confirm it:

```markdown
# Alt Text Manifest — <Project / folder name>
Generated: <date> | Context source: <document / context file / report label>
People policy: <omit / describe>

| # | File | Category | Alt text | Notes |
|---|------|----------|----------|-------|

## Long descriptions
### <filename>
<long description for each complex image>
```

**The Notes column is the exception, not the rule — default to empty; most rows have no note.** A note
records something **specific to that one image** that the publisher needs to know — an *observation
about the image*, never an instruction. The deliverable goes to a designer: do **not** dictate their
choices or restate the accessibility rules. Applying the people policy is the standing default and is
**not** a note; and lines like "use alt='' if placed as decoration" or "describe if it illustrates a
point" just tell the designer their own job — leave them out. Legit notes are factual flags: a one-line
reason a decorative image carries no information ("section-divider texture"), an unconfirmed proper
noun or title block ("reads 'Sheet A2.1', not verified"), a context-file override, a rotated source, a
duplicate/near-duplicate of another image, or a content-vs-folder mismatch (possible misfile).
**Never** put manifest-internal navigation ("see long description below"); the generator strips it, but
don't write it. Anything that applies to the whole set (e.g. "this folder is generic stock imagery")
goes **once** into the Step 5 report, not onto every row.

## Step 5: Verification pass + operational flags

Each worker re-views its own folder before returning: for every image, **could a screen-reader user
reconstruct what matters, in this document?** Revise entries that fail, and pass back operational flags.

The main thread then compiles one report to the user: total processed, count per category, and
**operational issues that affect publication** — rotated source files, content that doesn't match its folder's theme (possible
misfile), duplicate/near-duplicate images, mislabeled title blocks, and a heads-up on which images are
generic/stock (whether those need alt text or `alt=""` depends on where they land in the layout — the
publisher's call, not the manifest's).

Finally, **offer the finishing options** the user didn't already settle with a flag: thumbnails
embedded beside each entry (`--thumbs`) — if they say yes, regenerate the affected `.docx` with
thumbnails; and note that the master index was included by default, offering `--xlsx` if they'd rather
have a spreadsheet than the CSV (or `--no-index` if they don't want it at all).

## Step 6: Produce the `.docx` deliverable (the only per-folder output in the folder)

Convert each folder's scratch manifest into its `.docx`, written into the image folder, named with the
**enclosing folder name prepended** so files stay unique when collected:

```bash
python scripts/manifest_to_docx.py "<scratch manifest.md>" \
    --out "<imageFolder>/<folder name> alt-text-manifest.docx" \
    --subtitle "$report_label"
```

(First run only: `python3 -m venv .venv && .venv/bin/pip install python-docx`, then call
`.venv/bin/python` — see `scripts/README.md`.)

The `.docx` uses a standard per-image format — heading `Image N. <file>`, then **Category**, **Alt
text**, **Long description** (complex only), and **Note** (only when the row has one). Do **not** leave
a `.md` in the deliverable folder. The generator prints `OK  rows=N …` and flags any orphaned
long-descriptions or missing thumbnails — that line is your confirmation. **Don't render or introspect
the `.docx` to re-verify it**; investigate only when the generator prints a warning. (Rendering a sample
to eyeball layout — LibreOffice `soffice --headless --convert-to pdf`, or macOS `qlmanage` — is a
one-off development check, not something to do on every run.)

### Thumbnails beside each entry (`--thumbs`)

When `--thumbs` is set (or the user asks for a visual reference), build each `.docx` with a thumbnail so
every entry is laid out as *thumbnail | description*. Point the generator at the images (and, for
PDF-page rows, the rasterized pages):

```bash
python scripts/manifest_to_docx.py "<scratch manifest.md>" \
    --out "<imageFolder>/<folder name> alt-text-manifest.docx" \
    --subtitle "$report_label" \
    --thumbs --images-dir "<imageFolder>" --raster-dir "<scratchDir with rasterized PDF pages>"
```

Thumbnails are downscaled and EXIF-rotated (needs Pillow: `.venv/bin/pip install Pillow`). Rows whose
image can't be found are reported and fall back to text-only.

### Master index across all folders (default)

Unless `--no-index` was given, **always finish by building one overall index** from the shared scratch
dir holding the manifests — one row per image, columns Folder / # / File / Category / Alt chars / Alt
text / Long description / Notes. Write it to the top-level `$images_dir` as `alt-text-index.csv` (the
default), or `.xlsx` when `--xlsx` is set:

```bash
python scripts/manifest_to_index.py "<scratch dir of manifests>" \
    --out "<images_dir>/alt-text-index.csv"        # or alt-text-index.xlsx with --xlsx
```

`.csv` needs nothing; `.xlsx` (frozen header + autofilter) needs `openpyxl`. If `--xlsx` is requested
but openpyxl isn't installed, the script auto-writes `.csv` instead and says so.

## Out of scope

Generation and insertion are separate. Do not modify the target document unless the user explicitly
asks after reviewing the `.docx`.
