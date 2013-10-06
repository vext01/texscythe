#!/bin/sh
PYTHON=python2.7

echo ">>> texlive_texmf-minimal"
${PYTHON} texscyther --subset -i scheme-tetex:run -o PLIST-minimal -p share/

echo ">>> texlive_texmf-full"
${PYTHON} texscyther --subset -i scheme-full:run -x scheme-tetex -o PLIST-full -p share/

echo ">>> texlive_texmf-docs"
${PYTHON} texscyther --subset -i scheme-full:doc -o PLIST-doc -p share/

# for sanity check, should be the same as all of the above concatenated
echo ">>> sanity"
${PYTHON} texscyther --subset -i scheme-full:run,doc -o PLIST-sanity -p share/

# Note that PLIST-context is just the result of grepping for 'context' in
# PLIST-main and PLIST-full. The files in PLIST-context are then removed
# from the other packing lists. Not ideal, but I can't think of any other
# way...
