#!/usr/bin/env bash
# Rasterize every page of a PDF to PNGs, cross-platform.
#
# Usage:  pdf_to_pngs.sh <file.pdf> <outDir> [targetWidthPx=2000]
# Output: "<outDir>/<pdf-basename> - pNN.png"  (one per page, 1-based, zero-padded)
#
# Picks the first available backend, in order:
#   1. pdftoppm   (poppler)        — best quality, honors target width
#   2. magick / convert (ImageMagick)
#   3. osascript pdf_to_pngs.js     (native macOS PDFKit; no extra install)
#
# Rationale: `sips` and `qlmanage` only rasterize page 1 of a multi-page PDF.
set -euo pipefail

pdf="${1:?usage: pdf_to_pngs.sh <file.pdf> <outDir> [targetWidthPx]}"
outdir="${2:?usage: pdf_to_pngs.sh <file.pdf> <outDir> [targetWidthPx]}"
width="${3:-2000}"
here="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$outdir"
base="$(basename "$pdf")"; base="${base%.*}"

if command -v pdftoppm >/dev/null 2>&1; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  pdftoppm -png -scale-to-x "$width" -scale-to-y -1 "$pdf" "$tmp/page"
  for f in "$tmp"/page-*.png; do
    n="${f##*page-}"; n="${n%.png}"; n=$((10#$n))
    printf -v pn "%02d" "$n"
    mv "$f" "$outdir/$base - p$pn.png"
  done
  echo "$base: rasterized with pdftoppm"
elif command -v magick >/dev/null 2>&1 || command -v convert >/dev/null 2>&1; then
  bin="magick"; command -v magick >/dev/null 2>&1 || bin="convert"
  "$bin" -density 150 "$pdf" -resize "${width}x" -scene 1 "$outdir/$base - p%02d.png"
  echo "$base: rasterized with $bin"
elif command -v osascript >/dev/null 2>&1; then
  osascript -l JavaScript "$here/pdf_to_pngs.js" "$pdf" "$outdir" "$width"
else
  echo "No PDF rasterizer found. Install poppler (pdftoppm) or ImageMagick, or run on macOS." >&2
  exit 1
fi
