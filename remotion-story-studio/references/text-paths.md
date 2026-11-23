# Font outlines and neon text

Use the supplied text-outlines.ts helper: parse a font with opentype.js, shape supported glyphs, then generate explicit SVG M/L/Q/C/Z commands. The helper rejects missing glyphs and nonfinite geometry, and falls back to basic glyphs plus kerning when opentype.js cannot interpret an advanced GSUB lookup. Do not promise all decorative ligatures or real handwriting stroke order.

In Skia Web, MakeFromText may be typed but throw `Not implemented on React Native Web`. Feed generated SVG data to Skia.Path.MakeFromSVGString instead. This avoids an unavailable native API. The public runnable example uses SVG directly so it does not need Skia at all.

Older opentype.js toPathData optimizations produced nonfinite coordinates on repeated letters in some fonts. Explicit serialization of unmodified numeric commands is intentional. Test repeated letters and lowercase as well as a single uppercase word.

Animate using Remotion frames; do not use CSS keyframe animations. For SVG, compute getTotalLength once after paths mount, hold delayRender until it is ready, then drive dash offset from useCurrentFrame. For Skia, use each Path's end parameter with the same progress.

English fonts are not Chinese fonts. Validate charToGlyphIndex before drawing; offer a compatible font rather than quietly rendering empty squares. Local font names in this example are data keys, not installed OS font names.
