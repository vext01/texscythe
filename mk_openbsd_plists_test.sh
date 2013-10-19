#!/bin/sh
PYTHON=python2.7

BUILDSET_PKGS="scheme-basic:run"
# dblatex
BUILDSET_PKGS="${BUILDSET_PKGS} anysize:run appendix:run changebar:run"
BUILDSET_PKGS="${BUILDSET_PKGS} fancyvrb:run float:run footmisc:run"
BUILDSET_PKGS="${BUILDSET_PKGS} jknapltx:run multirow:run overpic:run"
BUILDSET_PKGS="${BUILDSET_PKGS} rotating:run stmaryrd:run subfigure:run"
BUILDSET_PKGS="${BUILDSET_PKGS} fancybox:run listings:run pdfpages:run"
BUILDSET_PKGS="${BUILDSET_PKGS} titlesec:run wasysym:run"
# gnustep/dbuskit, graphics/asymptote
BUILDSET_PKGS="${BUILDSET_PKGS} texinfo:run"
# gnusetp/dbuskit
BUILDSET_PKGS="${BUILDSET_PKGS} ec:run"
# graphics/asymptote
BUILDSET_PKGS="${BUILDSET_PKGS} epsf:run parskip:run"
# gnusetp/dbuskit, graphics/asymptote
BUILDSET_PKGS="${BUILDSET_PKGS} cm-super:run"
# lang/ghc,-docs
BUILDSET_PKGS="${BUILDSET_PKGS} zapfding:run symbol:run url:run eepic:run courier:run"
BUILDSET_PKGS="${BUILDSET_PKGS} times:run helvetic:run rsfs:run"
# devel/darcs
BUILDSET_PKGS="${BUILDSET_PKGS} preprint:run"

echo ">>> texlive_texmf-buildset"
echo ${BUILDSET_PKGS}
${PYTHON} texscyther --subset -i ${BUILDSET_PKGS} -o PLIST-buildset -p share/

# XXX below this line
#echo ">>> texlive_texmf-minimal"
#${PYTHON} texscyther --subset -i scheme-tetex:run -x scheme-basic -o PLIST-minimal -p share/

#echo ">>> texlive_texmf-full"
#${PYTHON} texscyther --subset -i scheme-full:run -x scheme-tetex -o PLIST-full -p share/

#echo ">>> texlive_texmf-docs"
#${PYTHON} texscyther --subset -i scheme-full:doc -o PLIST-doc -p share/

# for sanity check, should be the same as all of the above concatenated
#echo ">>> sanity"
#${PYTHON} texscyther --subset -i scheme-full:run,doc -o PLIST-sanity -p share/
