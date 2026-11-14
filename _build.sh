#!/bin/sh
set -e
Rscript -e "bookdown::render_book('index.Rmd', 'bookdown::gitbook')"
mkdir -p _book/assets && cp -r assets/icons _book/assets/
# device build guide (needs: pip install gitbuilding==0.14.9)
(cd build-guide && gitbuilding build-html) && rm -rf _book/build && cp -r build-guide/_site _book/build
