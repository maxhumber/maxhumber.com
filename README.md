# maxhumber.com

Small static blog. Markdown in, HTML out.

```sh
make build    # render input/ to output/
make preview  # build and serve locally
```

Posts live in `input/`:

```yaml
---
title: Books 2026
date: 2026-12-31
tags: books
slug: books2026
---
```

`slug` defaults to the filename. Untagged posts render but do not appear on the index, tag pages, or feeds.

```sh
make image IMG=~/Desktop/books_2026.png
```

Converts an image to a 900px JPEG in `input/images/`. 

Push `master` to deploy with GitHub Pages.
