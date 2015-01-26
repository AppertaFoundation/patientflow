#!/bin/bash

# compile the CSS file
lessc ../src/etake_style.less > css/etake_style.css

# lint over the files
csslint css/etake_style.css

# generate the styleguide
python generate_styleguide.py

# use UnCSS to ensure that all styles are used
uncss styleguide.html > ../../../src/css/etake_style.css  --ignoreSheets css/oe_base.css
diff --suppress-common-lines -i -E -b -B -w css/etake_style.css ../../../src/css/etake_style.css

echo "## Minifying UnCSS'd file"
lessc ../../../src/css/etake_style.css ../../../src/css/etake_style.css -x

filesize="$(du -h ../../../src/css/etake_style.css | cut -f1)"
echo "Resulting file is ${filesize}B"