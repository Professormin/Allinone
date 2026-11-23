# Setup and editable parameters

Require a new, empty output directory. `create_project.py` refuses to overwrite a nonempty project. Run the helper with Python, not as a bare executable. Dependencies are pinned; do not partially upgrade @remotion packages.

The included template uses Remotion 4.0.545, React 19.3.1, Zod 4.6.7 and opentype.js 2.0.0. Run the provided checks on the actual environment rather than assuming these versions remain current. For later upgrades, consult https://www.remotion.dev/docs and keep Remotion package versions identical.

Preview: `npm run dev`. Choose NeonText or StoryComic. Escape deselects a layer and exposes Composition > Default Props. Input values edited in Studio may be written back to source depending on Studio version; inspect current source before follow-up changes. CLI renders use source defaults unless --props supplies JSON.

For an existing project, add source components and registrations surgically. Preserve the user's custom text, colors, fps, resolution and duration. Check package-lock before choosing a package manager.

Fonts are bundled into each created project after download, so renders do not depend on a remote font service. Optional user CJK fonts belong to project public/fonts and the font manifest; only share them when licensed for redistribution.
