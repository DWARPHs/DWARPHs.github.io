# DWARPHs.github.io

Source for the [DWARPH documentation](https://dwarphs.github.io/), built with
[bookdown](https://bookdown.org/yihui/bookdown/).

## Layout

| File | Chapter |
| --- | --- |
| `index.Rmd` | What is DWARPH? |
| `01-modules.Rmd` | Modules and repositories |
| `02-build-install.Rmd` | Building and installation |
| `03-user-manual.Rmd` | User manual |
| `04-schedule-builder.Rmd` | Schedule builder (interactive) |
| `05-reference.Rmd` | Technical reference |
| `99-community.Rmd` | Issues and community |

The schedule builder is a self-contained HTML/CSS/JS tool in
`assets/schedule-builder.html`, inlined into the chapter as a raw HTML block. It has
no dependencies and runs entirely in the reader's browser. If you change the schedule
format in the firmware, update the builder's validation rules to match.

Figures under `assets/placeholder-*.svg` are placeholders awaiting real photographs,
screenshots and diagrams.

Chapters are ordered by filename. `index.Rmd` carries the site metadata;
`_output.yml` and `_bookdown.yml` hold the build configuration.

## Building locally

Requires R and pandoc.

```bash
Rscript -e 'install.packages(c("bookdown", "tibble", "knitr"))'
./_build.sh
./_serve.sh   # then open http://localhost:8000
```

## Deployment

Pushing to `main` triggers `.github/workflows/build-deploy.yml`, which renders the
book and publishes `_book/` to GitHub Pages. There is no build output committed to
the repository.
