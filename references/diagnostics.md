# Diagnostics

- Inspector shows Sequence: press Escape, select Composition, expand Default Props and right sidebar. Do not confuse layer transforms with composition input fields.
- TypeScript passes but Skia text fails: use opentype SVG outlines, not an unimplemented Web MakeFromText call.
- Missing font characters: pick a compatible authorized font; do not silently drop the characters.
- FFmpeg exit 3221225477 on Windows: test the exact bundled ffmpeg.exe with -version independently of React. If even this crashes, the native binary or environment is the failing layer. Inspect current official options before configuring another encoder. Use an absolute binaries directory because encoding may run with a temporary cwd. The public package does not ship old 2018 encoders or force a global FFmpeg change.
- Browser/DevTools ErrorEvent before the same original composition renders: test local browser connectivity and applicable execution permissions. Distinguish sandbox/network failure from a composition bug.
- Render is blank: hold delayRender for fonts and SVG path measurements, continue/cancel it on success/error, and inspect an actual exported still.

Never replace the user's folder with an unverified copied template. If a source project is missing during archival, record that fact and rebuild a clean example; do not call a reconstruction the recovered original.

Render scripts scope TMP/TEMP/TMPDIR to the generated project work/temp directory. Parent system settings are not changed.
