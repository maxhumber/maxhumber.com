<a href="https://maxhumber.com/">
  <img src="assets/static/signature.png" height="31">
</a>

#### About

My stupidly bespoke static site generator

#### Usage

- `make build` — render `input/*.md` into `output/`
- `make preview` — build, then serve at http://localhost:8000

Every build wipes `output/` first, so stale pages never linger.

Pushing to `master` builds and deploys to GitHub Pages via `.github/workflows/deploy.yml`.

#### Posts

One markdown file per post in `input/`, with frontmatter:

```
---
title: Books 2024
date: 2024-12-31
tags: books
slug: books2024
---
```

`slug` sets the URL and defaults to the filename — set it only to override.
Untagged posts still render, but stay off tag pages, feeds, and the index.

#### Images

```
make image IMG=~/Desktop/books_2025.png
```

Resizes to 900px wide, converts to JPEG, and drops it in `input/images/`.
Reference it as `images/books_2025.jpg`. Uses `sips`, which ships with macOS.
