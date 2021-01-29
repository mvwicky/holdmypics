# TODO

- [ ] More image variations
  - Tiled images
- [ ] _Animation_
- [ ] Make it possible to specify the image format using the `Accept` header, e.g., `Accept: image/webp` produces a `webp` image
  - This might be present some routing issues
- [ ] Refactor out image creation stuff into a library
- [ ] Write more tests. Basically download an image from every endpoint/argument combination and verify.
  - e.g., open the file w/ Pillow and make sure the colors/alpha are right
