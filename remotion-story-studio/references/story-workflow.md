# Plot to character story

1. Read the user-selected aspect ratio, duration and output root. If unspecified, propose a brief default and continue reversible work. A particular character, discipline or style is not the public product boundary.
2. Keep a private character bible: identity reference, wardrobe, signature accessories, anatomical side, allowed changes and visual style. The supplied character.example.json has no personal character data.
3. Turn the plot into a small causal sequence. Each scene needs image prompt, caption/dialogue, seconds and camera. Do not invent the user's exact wording.
4. Generate each scene using the actual image-generation tool with authorized reference images. Reuse accepted scene references when visual continuity matters. If no tool exists, stop the image-generation step accurately and allow user-provided files; do not create fake asset paths or claim prompts are images.
5. Inspect left/right accessories, clothing, hair, faces, paws/hands and scene continuity. Repair errors through the available image-editing tool before use. Reference conditioning improves but does not guarantee identity consistency.
6. Save each episode to a new public/stories/<episode>/ directory in the user's private project. Overlay exact captions in Remotion; ask the image model for text-free art.
7. Pass a real scenes JSON to StoryComic. Render a still at the first scene and a cut; then export MP4 and check dimensions/duration. The included assembly validator checks JSON, path containment and image existence before rendering.

The assistant orchestrates this from the chat. Remotion does not call the chat model or image model merely because a text field exists. Continuous character animation requires a separate video model and its actual credentials/authorization; keep that outside the default motion-comic workflow.
