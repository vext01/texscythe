#!/bin/sh
PYTHON=python2.7

echo ">>> texlive_texmf-minimal"
${PYTHON} texscyther --subset -i scheme-tetex:run -o PLIST-minimal

echo ">>> texlive_texmf-full"
${PYTHON} texscyther --subset -i scheme-full:run -x scheme-tetex -o PLIST-full

echo ">>> texlive_texmf-full"
${PYTHON} texscyther --subset -i scheme-full:doc -o PLIST-docs

# for sanity check, should be the same as all of the above concatenated
echo ">>> sanity"
${PYTHON} texscyther --subset -i scheme-full:run,doc -o PLIST-sanity
