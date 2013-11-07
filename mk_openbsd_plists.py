#!/usr/bin/env python2.7
#
# This is how we generate (a basis for) the OpenBSD packing lists for TeX Live.
#
# Note that the script does duplicate work. Future work should try to avoid
# this, but since the script doesn't take an age to run, this is fine for now.

import os, sys

class NastyError(Exception): pass

# This is how we detect manual pages
MAN_REGEX="texmf-dist\/doc\/man\/man1\/.*[0-9]$"

def run_texscyther(inc_specs, exc_specs, plist, global_re=""):
    if inc_specs:
        inc_specs = [ "'%s'" % x for x in inc_specs ]
        inc_specs = "-i " + " ".join(inc_specs)
    else:
        inc_specs = ""

    if exc_specs:
        exc_specs = [ "'%s'" % x for x in inc_specs ]
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
minimal_specs = runs_and_mans(["scheme-tetex"])
run_texscyther(minimal_specs, buildset_specs, "PLIST-minimal")


# /----------------------------------------------------------
# | FULL
# +----------------------------------------------------------
# | Everything bar docs (other than relevant manuals)
# \----------------------------------------------------------

print(">>> texlive_texmf-full")
full_specs = runs_and_mans(["scheme-full"])
run_texscyther(full_specs, minimal_specs, "PLIST-full")

# /----------------------------------------------------------
# | DOCS
# +----------------------------------------------------------
# | All remaining docs
# \----------------------------------------------------------

# exclude manuals and dumb pdf manuals
MAN_PDFMAN_REGEX="(?!texmf-dist\/doc\/man\/man[0-9]\/(.*[0-9]|.*.man[0-9].pdf)$)"

print(">>> texlive_texmf-docs")
run_texscyther(["scheme-full:doc"], [], "PLIST-doc", MAN_PDFMAN_REGEX)
