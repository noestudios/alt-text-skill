---
name: alt-text
description: Generate accessible alt text for a directory of images (or a parent folder of project subfolders), for inclusion in a document. Classifies each image (decorative, informative, functional, complex, text-as-image), applies WCAG-aligned writing rules, rasterizes PDF/rendering figures so they can be described, and outputs a standard-format .docx per folder for layout hand-off. Use when the user asks for alt text, image descriptions, or accessibility text for images.
argument-hint: [images-dir] [report-label] [document-path]
arguments: [images_dir, report_label, document]
disable-model-invocation: true
allowed-tools: Read Glob Grep Bash Write
---

# Alt Text Generator

Generate accessible alt text for every image in `$images_dir`, grounded in document context, and
deliver the results as a standard-format **`.docx`** per folder that a designer copy-pastes into
InDesign (or similar). The Markdown manifest is an internal working file only — see Step 4.

Bundled helpers live in `scripts/` (see `scripts/README.md`): `manifest_to_docx.py` builds the
`.docx`; `pdf_to_pngs.sh` rasterizes PDF pages so they can be viewed and described.

## Step 1: Resolve context (required before generating anything)

Never generate alt text without at least a document purpose. Resolve:

1. **Report label** (`$report_label`): the report/publication name, used as the `.docx` subtitle
   (e.g., "Acme 2025 Sustainability Report"). If not supplied as an argument, ask once.
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

- **Folder mode:** if `$images_dir` is a *parent* whose subfolders each hold a project's images,
  process **each subfolder as its own deliverable** (its own `.docx`). For many subfolders, fan out
  one worker per subfolder. Loose images sitting directly in the parent form their own deliverable.
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
receives only the `.docx` (Step 6).

Manifest format:

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

**Notes column carries only real, image-specific information** — justification for a decorative
classification, an uncertainty flag, a context override, the people-policy application, a rotated
source, a duplicate, a mislabeled title block, or a decorative-vs-informative recommendation for stock
imagery. **Never** put manifest-internal navigation ("see long description below") in the notes; the
generator strips it, but don't write it. If an image needs no note, leave the cell empty.

## Step 5: Verification pass + operational flags

After all images are written, re-view each against its drafted alt: **could a screen-reader user
reconstruct what matters, in this document?** Revise entries that fail.

Then report to the user: total processed, count per category, and **operational issues that affect
publication** — rotated source files, content that doesn't match its folder's theme (possible
misfile), duplicate/near-duplicate images, mislabeled title blocks, and for generic/stock images a
placement-dependent `alt=""`-vs-descriptive recommendation.

## Step 6: Produce the `.docx` deliverable (the only output in the folder)

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
a `.md` in the deliverable folder. Verify a sample by rendering it (LibreOffice:
`soffice --headless --convert-to pdf "<file.docx>"`, or macOS `qlmanage -t -s 1500 -o <dir>
"<file.docx>"`) and reading the result.

## Out of scope

Generation and insertion are separate. Do not modify the target document unless the user explicitly
asks after reviewing the `.docx`.
