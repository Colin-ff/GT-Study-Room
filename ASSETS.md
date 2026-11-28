# Homepage assets

The forest, study-room scene, five feature images, book cover artwork and logo were generated for this project. Feature tools labelled Coming soon are reserved design entries, not implemented AI services.

Navigation arrow and close icons are from `@phosphor-icons/core` 2.1.1 (MIT). The corresponding license is included in `assets/icons/LICENSE`.

Keep picture assets under `assets/`; `build.py` copies them to `dist/assets/`. The interface remains static HTML, CSS and JavaScript. npm is optional for development tests and the preview server; the Python build does not require npm dependencies.

`book-pages.webp` is a generated photographic paper-edge texture used on the separate 3D page faces. The existing cover artwork also textures the spine and back. Book titles and numbers remain accessible HTML, and existing test IDs/storage keys are unchanged.
