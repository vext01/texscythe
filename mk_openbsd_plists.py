#!/usr/bin/env python2.7
#
# This is how we generate (a basis for) the OpenBSD packing lists
# for TeX Live.

import os, sys, sh, re
from texscythe import config, subset

class NastyError(Exception): pass

def do_subset(**kwargs):
    cfg = config.Config(**kwargs)
    subset.compute_subset(cfg)

# Collect runfiles and manuals of a packages
MAN_REGEX="texmf-dist\/doc\/man\/man[0-9]\/.*[0-9]$"
def runs_and_mans_single(pkg):
    return [("{0}:run".format(pkg)), "{0}:doc:{1}".format(pkg, MAN_REGEX)]

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
    ]

print(">>> texlive_texmf-buildset")
buildset_specs = runs_and_mans(buildset_pkgs)
do_subset(
        inc_pkgspecs=buildset_specs,
        plist="PLIST-buildset",
        prefix_filenames="share/"
        )
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
context_specs = runs_and_mans(context_pkgs)
do_subset(
        inc_pkgspecs=context_specs,
        plist="PLIST-context",
        prefix_filenames="share/"
        )
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
minimal_specs = runs_and_mans(minimal_pkgs)
do_subset(
        inc_pkgspecs=minimal_specs,
        exc_pkgspecs=buildset_pkgs + context_pkgs,
        plist="PLIST-minimal",
        prefix_filenames="share/",
        )
#find_manuals_not_docfiles(minimal_pkgs, buildset_pkgs + context_pkgs)
print("\n\n")

# /----------------------------------------------------------
# | FULL
# +----------------------------------------------------------
# | Everything bar docs (other than relevant manuals)
# \----------------------------------------------------------

print(">>> texlive_texmf-full")
full_pkgs = ["scheme-full"]
full_specs = runs_and_mans(full_pkgs)
do_subset(
        inc_pkgspecs=full_specs,
        exc_pkgspecs=minimal_pkgs + buildset_pkgs + context_pkgs,
        plist="PLIST-full",
        prefix_filenames="share/",
        )
#find_manuals_not_docfiles(full_pkgs, minimal_pkgs + buildset_pkgs + context_pkgs)
print("\n\n")

# /----------------------------------------------------------
# | DOCS
# +----------------------------------------------------------
# | All remaining docs
# \----------------------------------------------------------

# exclude manuals and dumb pdf manuals
NO_MAN_PDFMAN_REGEX="(?!texmf-dist\/doc\/man\/man[0-9]\/(.*[0-9]|.*.man[0-9].pdf)$)"

print(">>> texlive_texmf-docs")
doc_specs=["scheme-full:doc"]
do_subset(
        inc_pkgspecs=doc_specs,
        plist="PLIST-docs",
        regex=NO_MAN_PDFMAN_REGEX,
        prefix_filenames="share/",
        )
print("\n\n")

# /----------------------------------------------------------
# | SANITY CHECKING
# \----------------------------------------------------------

print(">>> sanity check")

# Check there is no overlap in any of the above lists
def check_no_overlap(list1, list2):
    print("Checking no overlap between %s and %s" % (list1, list2))

    with open(list1, "r") as f:
        set1 = set([ x.strip() for x in f.readlines()
            if not x.endswith("/\n")])

    with open(list2, "r") as f:
        set2 = set([ x.strip() for x in f.readlines()
            if not x.endswith("/\n")])

    diff = set1.intersection(set2)
    if diff:
        raise NastyError("Overlapping packing lists:\n%s" % diff)

# check each PLIST against each other for overlap
all_plists = ("PLIST-buildset", "PLIST-minimal", "PLIST-full",
    "PLIST-docs", "PLIST-context")
for (l1, l2) in [ (x, y) for x in all_plists for y in all_plists if x < y ]:
    check_no_overlap(l1, l2)

# Check the concatenation of the above plists is what we expect
print("Check everything included")
PDFMAN_REGEX="(?!texmf-dist\/doc\/man\/man[0-9]\/.*.man[0-9].pdf$)"
sanity_specs = ["scheme-full:run,doc"]
do_subset(
        inc_pkgspecs=sanity_specs,
        plist="PLIST-sanitycheck",
        regex=PDFMAN_REGEX,
        prefix_filenames="share/",
        )

sh.sort(sh.cat(*all_plists), _out="PLIST-sanitycheck-actual")

# You can now diff the PLIST-sanitycheck against PLIST-sanitycheck-actual.
# Only directory names should be duplicated. If you see PDF manuals in here
# then they have probably been errorneously marked as runfiles instead of
# docfiles. Check the tlpdb and report upstream.

print("OK!")
