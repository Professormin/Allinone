---
name: remotion-story-studio
description: Use when creating reusable Remotion video templates, editable neon text paths, or character-consistent storyboard videos from a plot and reference images. Covers local previews, font choices, rendering and chat-driven image generation; not a standalone text-to-video model.
---

# Remotion Story Studio

Build parameterized videos and reusable character-story workflows. Honor the user's output root, aspect ratio, style and existing project edits. A private character is a configuration, not the boundary of this skill.

## Route the request
- New project or runnable example: run `python scripts/create_project.py --output <new-empty-directory> --install`. This creates a small Remotion project with NeonText and StoryComic, pins matching Remotion packages, and downloads four open fonts plus their licenses. See [project setup](references/setup.md).
- Existing Skia project or editable text: read [text paths](references/text-paths.md). Do not overwrite an existing project's Root or its frame rate, duration or input values while adding a feature.
- Plot plus recurring characters: read [story workflow](references/story-workflow.md). Use real image-generation tools when available; the Remotion composition assembles generated images and does not itself create character actions.
- Render or preview failure: read [diagnostics](references/diagnostics.md).

## Essential behavior

Use a schema and inline defaultProps for fields the user should edit. If the right inspector says Sequence and hides Default Props, press Escape to deselect the layer; inspect Composition > Default Props. Expand that section or the right sidebar if collapsed. Do not send the user searching for a universal standalone Props tab.

Convert font outlines to paths before animation. Skia Web can expose MakeFromText in TypeScript while throwing at runtime. Use the supplied opentype.js outline helper to generate SVG paths, then render SVG or Skia paths. Native-looking declarations do not prove Web support.

Preserve source fonts and licenses. English decorative fonts may not contain Chinese glyphs. Add a user-authorized local CJK font through project configuration; do not redistribute Windows fonts in the public skill.

Keep a character bible and all reference pictures outside the public skill. Express invariants such as signature accessories and anatomical left/right in that private configuration. Check every generated scene and repair drift before rendering.

A successful deliverable includes the actual image/video files, render result, dimensions/duration and usable local paths. Never equate a prompt, a generated JSON file, a TypeScript pass, or a prepared publication package with completed video generation or public release.

## Invocation examples

`$remotion-story-studio Create a neon title with an editable font menu.`

`$remotion-story-studio Turn this plot and my character references into a 16:9 motion comic. Save outputs under my configured project directory.`

Read only the references relevant to the chosen route. Generated media stays in the user's project; the installable skill contains no user identity or fixed personal output path.
