#!/usr/bin/env python2.7
#
# This is how we generate (a basis for) the OpenBSD packing lists
# for TeX Live.

import os, sys, re
from texscythe import config, subset

# Files from our preenerated 'texmf-var' tarball.
# This may change from year to year.
TEXMF_VAR_FILES = [
    "share/texmf-var/",
    "share/texmf-var/fonts/",
    "share/texmf-var/fonts/map/",
    "share/texmf-var/fonts/map/dvipdfmx/",
    "share/texmf-var/fonts/map/dvipdfmx/updmap/",
    "share/texmf-var/fonts/map/dvipdfmx/updmap/kanjix.map",
    "share/texmf-var/fonts/map/dvips/",
    "share/texmf-var/fonts/map/dvips/updmap/",
    "share/texmf-var/fonts/map/dvips/updmap/builtin35.map",
    "share/texmf-var/fonts/map/dvips/updmap/download35.map",
    "share/texmf-var/fonts/map/dvips/updmap/ps2pk.map",
    "share/texmf-var/fonts/map/dvips/updmap/psfonts.map",
    "share/texmf-var/fonts/map/dvips/updmap/psfonts_pk.map",
    "share/texmf-var/fonts/map/dvips/updmap/psfonts_t1.map",
    "share/texmf-var/fonts/map/pdftex/",
    "share/texmf-var/fonts/map/pdftex/updmap/",
    "share/texmf-var/fonts/map/pdftex/updmap/pdftex.map",
    "share/texmf-var/fonts/map/pdftex/updmap/pdftex_dl14.map",
    "share/texmf-var/fonts/map/pdftex/updmap/pdftex_ndl14.map",
    "share/texmf-var/fonts/map/pxdvi/",
    "share/texmf-var/fonts/map/pxdvi/updmap/",
    "share/texmf-var/web2c/",
    "share/texmf-var/web2c/aleph/",
    "share/texmf-var/web2c/aleph/aleph.fmt",
    "share/texmf-var/web2c/aleph/lamed.fmt",
    "share/texmf-var/web2c/eptex/",
    "share/texmf-var/web2c/eptex/eptex.fmt",
    "share/texmf-var/web2c/eptex/platex.fmt",
    "share/texmf-var/web2c/euptex/",
    "share/texmf-var/web2c/euptex/euptex.fmt",
    "share/texmf-var/web2c/euptex/uplatex.fmt",
    "share/texmf-var/web2c/luatex/",
    "share/texmf-var/web2c/luatex/dvilualatex.fmt",
    "share/texmf-var/web2c/luatex/dviluatex.fmt",
    "share/texmf-var/web2c/luatex/lualatex.fmt",
    "share/texmf-var/web2c/luatex/luatex.fmt",
    "share/texmf-var/web2c/metafont/",
    "share/texmf-var/web2c/metafont/mf.base",
    "share/texmf-var/web2c/pdftex/",
    "share/texmf-var/web2c/pdftex/amstex.fmt",
    "share/texmf-var/web2c/pdftex/cont-en.fmt",
    "share/texmf-var/web2c/pdftex/cslatex.fmt",
    "share/texmf-var/web2c/pdftex/csplain.fmt",
    "share/texmf-var/web2c/pdftex/eplain.fmt",
    "share/texmf-var/web2c/pdftex/etex.fmt",
    "share/texmf-var/web2c/pdftex/jadetex.fmt",
    "share/texmf-var/web2c/pdftex/latex.fmt",
    "share/texmf-var/web2c/pdftex/mex.fmt",
    "share/texmf-var/web2c/pdftex/mllatex.fmt",
    "share/texmf-var/web2c/pdftex/mltex.fmt",
    "share/texmf-var/web2c/pdftex/mptopdf.fmt",
    "share/texmf-var/web2c/pdftex/pdfcslatex.fmt",
    "share/texmf-var/web2c/pdftex/pdfcsplain.fmt",
    "share/texmf-var/web2c/pdftex/pdfetex.fmt",
    "share/texmf-var/web2c/pdftex/pdfjadetex.fmt",
    "share/texmf-var/web2c/pdftex/pdflatex.fmt",
    "share/texmf-var/web2c/pdftex/pdfmex.fmt",
    "share/texmf-var/web2c/pdftex/pdftex.fmt",
    "share/texmf-var/web2c/pdftex/pdfxmltex.fmt",
    "share/texmf-var/web2c/pdftex/texsis.fmt",
    "share/texmf-var/web2c/pdftex/utf8mex.fmt",
    "share/texmf-var/web2c/pdftex/xmltex.fmt",
    "share/texmf-var/web2c/ptex/",
    "share/texmf-var/web2c/ptex/ptex.fmt",
    "share/texmf-var/web2c/tex/",
    "share/texmf-var/web2c/tex/tex.fmt",
    "share/texmf-var/web2c/uptex/",
    "share/texmf-var/web2c/uptex/uptex.fmt",
    "share/texmf-var/web2c/xetex/",
    "share/texmf-var/web2c/xetex/cont-en.fmt",
    "share/texmf-var/web2c/xetex/xelatex.fmt",
    "share/texmf-var/web2c/xetex/xetex.fmt",
]

class NastyError(Exception): pass

def do_subset(**kwargs):
    cfg = config.Config(**kwargs)
    return subset.compute_subset(cfg)

# Collect runfiles and manuals of a packages
MAN_INFO_REGEX="texmf-dist\/doc\/(man\/man[0-9]\/.*[0-9]|info\/.*\.info)$"
def runs_and_mans_single(pkg):
    return [("{0}:run".format(pkg)), "{0}:doc:{1}".format(pkg, MAN_INFO_REGEX)]

# Collect runfiles and manuals of a list of packages
def runs_and_mans(pkglist):
    specs = []
    for pkg in pkglist:
        specs.extend(runs_and_mans_single(pkg))
    return specs

def find_manuals_not_docfiles(incpkgs, excpkgs=[]):
    print("Checking for manuals which are not docfiles...")

    incspecs = [ "%s:run,src,bin" % p for p in incpkgs ]
    excspecs = [ "%s:run,src,bin" % p for p in excpkgs ]
    cfgp = config.Config(inc_pkgspecs=incspecs, exc_pkgspecs=excspecs, plist=None)

    files = subset.compute_subset(cfgp)
    regex = "texmf-dist\/doc\/man\/man[0-9]\/(.*.man[0-9].pdf|.*\.1)$"
    bad = [ x for x in files if re.match(regex, x) ]

    if bad:
        print(" [ FAIL ]\nManual pages are not categorised as docfiles:\n")
        for f in bad:
            print("  " + f)
    else:
        print(" [ OK ]\n")

def writelines(fh, lines):
    for i in lines: fh.write(i + "\n")

def write_plist(files, filename, top_matter=[], bottom_matter=[]):
    with open(filename, "w") as fh:
        writelines(fh, top_matter)
        writelines(fh, files)
        writelines(fh, bottom_matter)

# Stuff which is ported separately from texlive in OpenBSD
never_pkgs = ["asymptote", "latexmk", "texworks"]

# /-------------------------------------
# | BUILDSET
# +-------------------------------------
# | A minimal subset for building ports.
# \-------------------------------------
buildset_pkgs = [
	"scheme-basic",
	# dblatex
    "anysize", "appendix", "changebar",
    "fancyvrb", "float", "footmisc",
    "jknapltx", "multirow", "overpic",
    "rotating", "stmaryrd", "subfigure",
    "fancybox", "listings", "pdfpages",
    "titlesec", "wasysym",
    # gnustep/dbuskit, graphics/asymptote
    "texinfo",
    # gnusetp/dbuskit
    "ec",
    # graphics/asymptote
    "epsf", "parskip",
    # gnusetp/dbuskit, graphics/asymptote
    "cm-super",
    # lang/ghc,-docs
    "zapfding", "symbol", "url", "eepic", "courier",
    "times", "helvetic", "rsfs",
    # devel/darcs
    "preprint",
    # print/lilypond (indirect via fonts/mftrace)
    "metapost",
    ]

print(">>> texlive_texmf-buildset")
buildset_specs = runs_and_mans(buildset_pkgs)
buildset_top_matter = [
    "@comment $OpenBSD$",
    "@conflict teTeX_texmf-*",
    "@conflict texlive_base-<2013",
    "@conflict texlive_texmf-docs-<2013",
    "@conflict texlive_texmf-minimal-<2013",
    "@conflict texlive_texmf-full-<2013",
    "@conflict texlive_texmf-context-<2013",
    "@pkgpath print/texlive/texmf-minimal",
    "@pkgpath print/teTeX/texmf",
]
buildset_files = do_subset(
        inc_pkgspecs=buildset_specs,
        exc_pkgspecs=never_pkgs,
        plist = None,
        prefix_filenames="share/"
        )
buildset_files = sorted(buildset_files + TEXMF_VAR_FILES)
write_plist(buildset_files, "PLIST-buildset", buildset_top_matter)
#find_manuals_not_docfiles(buildset_pkgs)
print("\n\n")

# /-------------------------------------
# | CONTEXT
# +-------------------------------------
# | Guess what?
# \-------------------------------------

# Get this list from the collection-context pkg.
# DO NOT INCLUDE DEPENDENCIES THAT WOULD APPEAR
# IN OTHER SUBSETS, E.g. 'collection-basic'. Generally
# you want all the depends that are prefixed "context-"
# and "context". Note the use of ! to not follow deps.
# This prevents us pulling in pdftex, xetex, ... again.
context_pkgs = [
        "!context",
        "!context-account",
        "!context-algorithmic",
        "!context-bnf",
        "!context-chromato",
        "!context-construction-plan",
        "!context-cyrillicnumbers",
        "!context-degrade",
        "!context-filter",
        "!context-fixme",
        "!context-french",
        "!context-fullpage",
        "!context-games",
        "!context-gantt",
        "!context-gnuplot",
        "!context-letter",
        "!context-lettrine",
        "!context-lilypond",
        "!context-mathsets",
        "!context-notes-zh-cn",
        "!context-rst",
        "!context-ruby",
        "!context-simplefonts",
        "!context-simpleslides",
        "!context-transliterator",
        "!context-typearea",
        "!context-typescripts",
        "!context-vim"
]

print(">>> PLIST-context")
context_top_matter = [
    "@comment $OpenBSD$",
    "@conflict teTeX_texmf-*",
    "@conflict texlive_base-<2013",
    "@conflict texlive_texmf-docs-<2013",
    "@conflict texlive_texmf-full-<2013",
    "@conflict texlive_texmf-buildset-<2013",
    "@conflict texlive_texmf-minimal-<2013",
]
context_bottom_matter = [
    "@unexec rm -Rf %D/share/texmf-var/luatex-cache",
    "@exec %D/bin/mtxrun --generate > /dev/null 2>&1",
    "@exec %D/bin/mktexlsr > /dev/null 2>&1",
    "@unexec-delete %D/bin/mktexlsr > /dev/null 2>&1",
]
context_specs = runs_and_mans(context_pkgs)
context_files = do_subset(
        inc_pkgspecs=context_specs,
        exc_pkgspecs=never_pkgs,
        plist=None,
        prefix_filenames="share/"
        )
write_plist(context_files, "PLIST-context",
        context_top_matter, context_bottom_matter)
#find_manuals_not_docfiles(context_pkgs)
print("\n\n")

# /----------------------------------------------------------
# | MINIMAL
# +----------------------------------------------------------
# | Scheme-tetex minus anything we installed in the buildset
# | (also no context)
# \----------------------------------------------------------

print(">>> texlive_texmf-minimal")
minimal_pkgs = ["scheme-tetex"]
minimal_top_matter = [
    "@comment $OpenBSD$",
    "@conflict teTeX_texmf-*",
    "@conflict texlive_base-<2013",
    "@conflict texlive_texmf-docs-<2013",
    "@conflict texlive_texmf-full-<2013",
    "@conflict texlive_texmf-buildset-<2013",
    "@conflict texlive_texmf-context-<2013",
    "@pkgpath print/teTeX/texmf",
]
minimal_bottom_matter = [
    "@exec %D/bin/mktexlsr > /dev/null 2>&1",
    "@unexec-delete %D/bin/mktexlsr > /dev/null 2>&1",
]
minimal_specs = runs_and_mans(minimal_pkgs)
minimal_files = do_subset(
        inc_pkgspecs=minimal_specs,
        exc_pkgspecs=buildset_pkgs + context_pkgs + never_pkgs,
        plist=None,
        prefix_filenames="share/",
        )
write_plist(minimal_files, "PLIST-main",
        minimal_top_matter, minimal_bottom_matter)
#find_manuals_not_docfiles(minimal_pkgs, buildset_pkgs + context_pkgs)
print("\n\n")

# /----------------------------------------------------------
# | FULL
# +----------------------------------------------------------
# | Everything bar docs (other than relevant manuals)
# \----------------------------------------------------------

print(">>> texlive_texmf-full")
full_pkgs = ["scheme-full"]
full_top_matter = [
    "@comment $OpenBSD$",
    "@conflict teTeX_texmf-*",
    "@conflict texlive_base-<2013",
    "@conflict texlive_texmf-docs-<2013",
    "@conflict texlive_texmf-minimal-<2013",
    "@conflict texlive_texmf-buildset-<2013",
    "@conflict texlive_texmf-contextt-<2013",
    "@pkgpath print/texlive/texmf-full",
    "@pkgpath print/teTeX/texmf",
]
full_bottom_matter = [
    "@exec %D/bin/mktexlsr > /dev/null 2>&1",
    "@unexec-delete %D/bin/mktexlsr > /dev/null 2>&1",
]
full_specs = runs_and_mans(full_pkgs)
full_files = do_subset(
        inc_pkgspecs=full_specs,
        exc_pkgspecs=minimal_pkgs + buildset_pkgs + context_pkgs + never_pkgs,
        plist=None,
        prefix_filenames="share/",
        )
write_plist(full_files, "PLIST-full", full_top_matter, full_bottom_matter)
#find_manuals_not_docfiles(full_pkgs, minimal_pkgs + buildset_pkgs + context_pkgs)
print("\n\n")

# /----------------------------------------------------------
# | DOCS
# +----------------------------------------------------------
# | All remaining docs
# \----------------------------------------------------------

# exclude manuals and dumb pdf manuals
NO_MAN_INFO_PDFMAN_REGEX="(?!texmf-dist\/doc\/(man\/man[0-9]\/(.*[0-9]|.*.man[0-9].pdf)|info\/.*\.info)$)"

print(">>> texlive_texmf-docs")
doc_specs=["scheme-tetex:doc"]
doc_top_matter = [
    "@comment $OpenBSD$",
    "@conflict teTeX_texmf-doc-*",
    "@conflict texlive_base-<2013",
    "@conflict texlive_texmf-minimal-<2013",
    "@conflict texlive_texmf-full-<2013",
    "@conflict texlive_texmf-buildset-<2013",
    "@conflict texlive_texmf-context-<2013",
    "@pkgpath print/texlive/texmf-docs",
    "@pkgpath print/teTeX_texmf,-doc",
]
doc_bottom_matter = [
    "@exec %D/bin/mktexlsr > /dev/null 2>&1",
    "@unexec-delete %D/bin/mktexlsr > /dev/null 2>&1",
]
doc_files = do_subset(
        inc_pkgspecs=doc_specs,
        exc_pkgspecs=never_pkgs,
        plist=None,
        regex=NO_MAN_INFO_PDFMAN_REGEX,
        prefix_filenames="share/",
        )
write_plist(doc_files, "PLIST-docs", doc_top_matter, doc_bottom_matter)
print("\n\n")

# /----------------------------------------------------------
# | SANITY CHECKING
# \----------------------------------------------------------

print(">>> sanity check")

# Check there is no overlap in any of the above lists
def read_plist_back(filename):
    with open(filename, "r") as f:
        set1 = set([ x.strip() for x in f.readlines()
            if (not x.endswith("/\n")) and (not x.startswith("@")) ])
    return set1

def check_no_overlap(list1, list2):
    print("Checking no overlap between %s and %s" % (list1, list2))

    set1 = read_plist_back(list1)
    set2 = read_plist_back(list2)

    if set1.intersection(set2):
        raise NastyError("Overlapping packing lists:\n%s" % diff)

# check each PLIST against each other for overlap
all_plists = ("PLIST-buildset", "PLIST-main", "PLIST-full",
    "PLIST-docs", "PLIST-context")
for (l1, l2) in [ (x, y) for x in all_plists for y in all_plists if x < y ]:
    check_no_overlap(l1, l2)

# Check the concatenation of the above plists is what we expect
#print("Check everything included")
#PDFMAN_REGEX="(?!texmf-dist\/doc\/man\/man[0-9]\/.*.man[0-9].pdf$)"
#sanity_specs = ["scheme-full:run,doc"]
#do_subset(
#        inc_pkgspecs=sanity_specs,
#        plist="PLIST-sanitycheck",
#        regex=PDFMAN_REGEX,
#        prefix_filenames="share/",
#        )
#
#import sh
#sh.sort(sh.cat(*all_plists), _out="PLIST-sanitycheck-actual")
#
# You can now diff the PLIST-sanitycheck against PLIST-sanitycheck-actual.
# Only directory names should be duplicated. If you see PDF manuals in here
# then they have probably been errorneously marked as runfiles instead of
# docfiles. Check the tlpdb and report upstream.

print("OK!")
