#!/usr/bin/env python2.7
#
# This is how we generate (a basis for) the OpenBSD packing lists for TeX Live.
#
# Note that the script does duplicate work. Future work should try to avoid
# this, but since the script doesn't take an age to run, this is fine for now.

import os, sys, sh

class NastyError(Exception): pass

def run_texscyther(inc_specs, exc_specs, plist, global_re=""):
    if inc_specs:
        inc_specs = [ "'%s'" % x for x in inc_specs ]
        inc_specs = "-i " + " ".join(inc_specs)
    else:
        inc_specs = ""

    if exc_specs:
        exc_specs = [ "'%s'" % x for x in exc_specs ]
        exc_specs = "-x " + " ".join(exc_specs)
    else:
        exc_specs = ""

    if global_re != "":
        global_re = "-r '%s'" % global_re

    cmd = "%s texscyther --subset %s %s -o %s %s" % (
        sys.executable, inc_specs, exc_specs, plist, global_re
        )
    print ("Running: %s" % cmd)
    if os.system(cmd) != 0:
        raise NastyError("texscyther failed")

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
run_texscyther(buildset_specs, [], "PLIST-buildset")

# /----------------------------------------------------------
# | MINIMAL
# +----------------------------------------------------------
# | Scheme-tetex minus anything we installed in the buildset
# \----------------------------------------------------------

print(">>> texlive_texmf-minimal")
minimal_pkgs = ["scheme-tetex"]
minimal_specs = runs_and_mans(minimal_pkgs)
run_texscyther(minimal_specs, buildset_pkgs, "PLIST-minimal")

# /----------------------------------------------------------
# | FULL
# +----------------------------------------------------------
# | Everything bar docs (other than relevant manuals)
# \----------------------------------------------------------

print(">>> texlive_texmf-full")
full_pkgs = ["scheme-full"]
full_specs = runs_and_mans(full_pkgs)
run_texscyther(full_specs, minimal_pkgs + buildset_pkgs, "PLIST-full")

# /----------------------------------------------------------
# | DOCS
# +----------------------------------------------------------
# | All remaining docs
# \----------------------------------------------------------

# exclude manuals and dumb pdf manuals
MAN_PDFMAN_REGEX="(?!texmf-dist\/doc\/man\/man[0-9]\/(.*[0-9]|.*.man[0-9].pdf)$)"

print(">>> texlive_texmf-docs")
run_texscyther(["scheme-full:doc"], [], "PLIST-doc", MAN_PDFMAN_REGEX)

# /----------------------------------------------------------
# | SANITY CHECKING
# \----------------------------------------------------------

print(">>> sanity check")

# Check there is no overlap in any of the above lists
def check_no_overlap(list1, list2):
    print("Checking no overlap between %s and %s" % (list1, list2))

    with open(list1, "r") as f:
        set1 = set([ x.strip() for x in f.readlines() if not x.endswith("/\n")])

    with open(list2, "r") as f:
        set2 = set([ x.strip() for x in f.readlines() if not x.endswith("/\n")])

    diff = set1.intersection(set2)
    if diff:
        raise NastyError("Overlapping packing lists:\n%s" % diff)

# check each PLIST against each other for overlap
all_plists = ("PLIST-buildset", "PLIST-minimal", "PLIST-full", "PLIST-doc")
for (l1, l2) in [ (x, y) for x in all_plists for y in all_plists if x < y ]:
    check_no_overlap(l1, l2)

# Check the concatenation of the above plists is what we expect
print("Check everything included")
PDFMAN_REGEX="(?!texmf-dist\/doc\/man\/man[0-9]\/.*.man[0-9].pdf$)"
run_texscyther(["scheme-full:run,doc"], [], "PLIST-sanitycheck", PDFMAN_REGEX)

sh.sort(sh.cat(*all_plists), _out="PLIST-sanitycheck-actual")
#check_no_overlap("PLIST-sanitycheck", "PLIST-sanitycheck-actual")

# You can now diff the PLIST-sanitycheck against PLIST-sanitycheck-actual.
# Only directory names should be duplicated. If you see PDF manuals in here
# then they have probably been errorneously marked as runfiles instead of
# docfiles. Check the tlpdb and report upstream.

print("OK!")
