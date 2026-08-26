// Rasterize each page of a PDF to a PNG using native macOS PDFKit (JXA + ObjC bridge).
// No poppler / ImageMagick / Ghostscript required — ships with macOS.
//
// Usage:
//   osascript -l JavaScript pdf_to_pngs.js <pdfPath> <outDir> [targetWidthPx=2000]
//
// Output: <outDir>/<pdf-basename> - pNN.png  (one file per page, zero-padded)
//
// Notes:
//   * `sips` and `qlmanage` only rasterize page 1 of a multi-page PDF — that is why this
//     script exists. If `pdftoppm` (poppler) or `magick` (ImageMagick) is installed they are
//     faster alternates for the same job; prefer them when available.
ObjC.import('Foundation');
ObjC.import('AppKit');
ObjC.import('Quartz'); // brings in PDFKit (PDFDocument / PDFPage)

function run(argv) {
  var pdfPath = argv[0];
  var outDir  = argv[1];
  var targetW = parseFloat(argv[2] || '2000');

  if (!pdfPath || !outDir) {
    return 'ERROR: usage: pdf_to_pngs.js <pdfPath> <outDir> [targetWidthPx]';
  }

  var fm = $.NSFileManager.defaultManager;
  fm.createDirectoryAtPathWithIntermediateDirectoriesAttributesError(outDir, true, $(), $());

  var url = $.NSURL.fileURLWithPath(pdfPath);
  var doc = $.PDFDocument.alloc.initWithURL(url);
  if (doc.isNil()) { return 'ERROR: could not load ' + pdfPath; }

  var n = doc.pageCount;
  var base = $(pdfPath).lastPathComponent.js.replace(/\.pdf$/i, '');
  var results = [];

  for (var i = 0; i < n; i++) {
    var page = doc.pageAtIndex(i);
    var box  = 0; // kPDFDisplayBoxMediaBox = 0
    var b = page.boundsForBox(box); // {origin,size} in points
    var w = b.size.width, h = b.size.height;
    if (w <= 0 || h <= 0) { results.push('page ' + (i + 1) + ': bad bounds'); continue; }
    var scale = targetW / w;
    var pxW = Math.round(w * scale), pxH = Math.round(h * scale);
    var size = $.NSMakeSize(pxW, pxH);

    var thumb = page.thumbnailOfSizeForBox(size, box); // NSImage rendered at that size
    var tiff  = thumb.TIFFRepresentation;
    var rep   = $.NSBitmapImageRep.imageRepWithData(tiff);
    // NSBitmapImageFileTypePNG = 4
    var png   = rep.representationUsingTypeProperties(4, $.NSDictionary.dictionary);

    var pad = ('0' + (i + 1)).slice(-2);
    var outPath = outDir + '/' + base + ' - p' + pad + '.png';
    var ok = png.writeToFileAtomically($(outPath), true);
    results.push('page ' + (i + 1) + ' -> ' + pxW + 'x' + pxH + ' ' + (ok ? 'OK' : 'WRITEFAIL'));
  }
  return base + ' (' + n + ' pages)\n' + results.join('\n');
}
