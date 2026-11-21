import type {Font, Path} from 'opentype.js';
const serialize = (path: Path): string => path.commands.map((c) => {
  const n = (v: number) => {if (!Number.isFinite(v)) throw new Error('Nonfinite font geometry'); return Number(v.toFixed(3));};
  switch(c.type) {
    case 'M': case 'L': return `${c.type}${n(c.x)} ${n(c.y)}`;
    case 'Q': return `Q${n(c.x1)} ${n(c.y1)} ${n(c.x)} ${n(c.y)}`;
    case 'C': return `C${n(c.x1)} ${n(c.y1)} ${n(c.x2)} ${n(c.y2)} ${n(c.x)} ${n(c.y)}`;
    case 'Z': return 'Z';
  }
}).join(' ');
export const textOutlines = (font: Font, text: string, size: number): string[] => {
  if (Array.from(text).some((c) => c !== ' ' && font.charToGlyphIndex(c) === 0)) throw new Error('Selected font does not contain this text. Choose a compatible font.');
  const paths: string[] = [];
  try {
    font.forEachGlyph(text, 0, 0, size, {kerning:true}, (g,x,y,s) => paths.push(serialize(g.getPath(x,y,s))));
    return paths.filter(Boolean);
  } catch(error) {
    if (!(error instanceof Error) || !error.message.includes('not yet supported')) throw error;
  }
  let x = 0;
  const glyphs = Array.from(text, c => font.charToGlyph(c));
  return glyphs.map((g,i) => {
    const d = serialize(g.getPath(x,0,size));
    const kern = glyphs[i+1] ? (font.getKerningValue(g,glyphs[i+1]) || 0) : 0;
    x += ((g.advanceWidth ?? font.unitsPerEm) + kern) * size / font.unitsPerEm;
    return d;
  }).filter(Boolean);
};
