# TODO

## Backend

- [ ] More image variations
  - [ ] Tiled images
  - [ ] Images made up of random colors
- [x] Cull cached image files based on the total size of saved files
  - Cache the size of each file per path (so we don't have to `stat` the same file over and over again)
- [ ] _Animation_
- [ ] Make it possible to specify the image format using the `Accept` header, e.g., `Accept: image/webp` produces a `webp` image
  - This might be present some routing issues
- [ ] Refactor out image creation stuff into a library
- [ ] Write more tests. Basically download an image from every endpoint/argument combination and verify.
  - e.g., open the file w/ Pillow and make sure the colors/alpha are right

## Frontend

- [ ] Replace `webpack` with `esbuild` (at least for the TypeScript parts)
