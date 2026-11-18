#!/bin/sh
set -e
Rscript -e "bookdown::render_book('index.Rmd', 'bookdown::gitbook')"
mkdir -p _book/assets && cp -r assets/icons _book/assets/
cp redirects/*.html _book/
# device build guide (needs: pip install gitbuilding==0.14.9)
(cd build-guide && gitbuilding build-html) && rm -rf _book/build && cp -r build-guide/_site _book/build
# page counts (analytics.html, also in header.html for the book): before </head> of each build guide page
python3 -c 'import pathlib; s = pathlib.Path("analytics.html").read_text()
for p in pathlib.Path("_book/build").rglob("*.html"):
    h = p.read_text()
    if "goatcounter" not in h and "</head>" in h: p.write_text(h.replace("</head>", s + "</head>", 1))'
