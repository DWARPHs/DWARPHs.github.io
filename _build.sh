#!/bin/sh
set -e
Rscript -e "bookdown::render_book('index.Rmd', 'bookdown::gitbook')"
mkdir -p _book/assets && cp -r assets/icons _book/assets/
