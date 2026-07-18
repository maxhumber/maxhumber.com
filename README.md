<a href="https://maxhumber.com/">
  <img src="assets/static/signature.png" height="31">
</a>

#### About

My stupidly bespoke static site generator

#### Usage

- `make build` — render `input/*.md` into `output/`
- `make preview` — build, then serve at http://localhost:8000
- `make clean` — delete `output/`

Pushing to `master` builds and deploys to GitHub Pages via `.github/workflows/deploy.yml`.

#### Images

Drop them in `input/images/`, resized to 900px wide. `sips` ships with macOS:

```
sips -Z 900 -s format jpeg -s formatOptions 85 big.png --out input/images/small.jpg
```

Prefer JPEG — the book collages saved as PNG run ~800KB versus ~130KB as JPEG.
