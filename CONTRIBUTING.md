# Contributing

Thanks for your interest in improving the alt-text skill.

## Ground rules

- **Accessibility first.** Changes to the writing rules should track WCAG guidance and the practical
  needs of screen-reader users. Cite the reasoning in the PR.
- **Keep the deliverable stable.** The `.docx` format is consumed by designers copy-pasting into
  layout tools; don't change field names or structure without a clear migration note.
- **Cross-platform.** New tooling should degrade gracefully — prefer widely available binaries
  (poppler, ImageMagick, LibreOffice) with sensible fallbacks.

## Dev setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Testing a change

- Run `alt-text/scripts/manifest_to_docx.py` against `examples/sample-manifest.md` and confirm the
  generated `.docx` matches `examples/sample-output.docx` (open both, or diff the extracted text). The
  committed sample uses `--subtitle "Acme 2025 Annual Report"`; without it only the subtitle line
  differs — compare the rest.
- If you touch PDF handling, test `alt-text/scripts/pdf_to_pngs.sh` on a multi-page PDF with each
  backend you have installed.

## Scope

This repo is the skill and its helper scripts. It does **not** insert alt text into target documents —
generation and insertion are intentionally separate.
