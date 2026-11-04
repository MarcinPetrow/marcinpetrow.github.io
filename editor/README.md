# Blog Editor

A dedicated GTK4/libadwaita desktop editor for this Astro blog. It reads and
writes posts in `content/posts/` and stores imported images in `public/images/`.

## Run

From the repository root:

```sh
./editor/blog-editor
```

To add **Blog Editor** to the Ubuntu application menu:

```sh
./editor/install-local.sh
```

The application requires Python 3, GTK4, libadwaita, WebKitGTK, PyGObject,
PyYAML, and Pillow. On Ubuntu these correspond to packages similar to
`python3-gi`, `gir1.2-gtk-4.0`, `gir1.2-adw-1`, `gir1.2-webkit-6.0`,
`python3-yaml`, and `python3-pil`.

## Features

- Browse and search all existing Markdown and MDX posts.
- Edit title, description, date, tags, draft state, cover image, and Markdown.
- See a live local preview without uploading content.
- Create new draft posts with safe filenames.
- Import images into `public/images/` and insert valid Astro Markdown links.
- Crop, rotate, resize, compress, and convert local images.
- Publish the current post and its referenced local images to `origin/master`.
- Update the local repository with a safe fast-forward-only pull.

Changes stay local until they are committed and pushed with Git.

`Publish` preserves the manually selected draft status. It commits only the
current post and images referenced by that post, so unrelated working-tree
changes are not included. `Update` saves the open post before pulling and
stops instead of overwriting files when Git detects a conflict.
