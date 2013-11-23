#!/usr/bin/env python2.7
# Copyright (c) 2013, Edd Barrett <edd@openbsd.org> <vext01@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# ---------------------------------
# Lint the TeX Live TLPDB database
# ---------------------------------

import os, sys, copy, re, os.path
from texscythe import config, subset, tlpdbparser

class LintError(Exception): pass

def do_subset(**kwargs):
    cfg = config.Config(**kwargs)
    subset.compute_subset(cfg)

def find_manuals_not_docfiles(cfg):
    sys.stdout.write("Checking for manuals which are not docfiles...")

    cfgp = copy.deepcopy(cfg)
    cfgp.inc_pkgspecs = [ pkg + ":run,src,bin" ]

    files = subset.compute_subset(cfgp)
    regex = "texmf-dist\/doc\/man\/man[0-9]\/(.*.man[0-9].pdf|.*\.1)$"
    bad = [ x for x in files if re.match(regex, x) ]

    if bad:
        sys.stdout.write(" [ FAIL ]\n" + 
            "Manual pages are not categorised as docfiles:\n")
        for f in bad:
            print("  " + f)
    else:
        sys.stdout.write(" [ OK ]\n")

def check_all_files_exist(files, tltree):
    sys.stdout.write("Checking all files exist...")

    bad = [ f for f in files 
            if not os.path.exists(os.path.join(tltree, f)) ]

    if bad:
        print(" [ FAIL ]\nThese files are absent in the texlive tree:")
        for f in bad:
            print("  %s" % f)
    else:
        print(" [ OK ]")

def looks_like_manual(path):
    # Try to guess if this file is a manual page.
    # For now we just see if it has what appears to be at-least two
    # section header tags.
    try:
        with open(path, "r") as fh:
            sh_count = 0
            for line in fh: # resist sucking in whole file
                if line.lower().startswith(".sh"):
                    sh_count += 1
                    if sh_count == 2:
                        return True
    except IOError: # missing files are caught elsewhere
        pass
    return False

def find_manuals_in_wrong_path(files, tltree):
    sys.stdout.write("Checking for manuals in wrong path...")

    bad = [ f for f in files
            if not f.startswith("texmf-dist/doc/man/man") and
            looks_like_manual(os.path.join(tltree, f)) ]

    if bad:
        print(" [ FAIL ]\nThese files look like manuals in the wrong path:")
        for f in bad:
            print("  %s" % f)
    else:
        print(" [ OK ]")

def find_windows_exes_not_binfiles(cfg):
    sys.stdout.write("Checking for windows .exes which are not binfiles...")

    cfgp = copy.deepcopy(cfg)
    cfgp.inc_pkgspecs = [ pkg + ":run,src,doc" ]

    files = subset.compute_subset(cfgp)
    regex = ".*\.exe$"
    bad = [ x for x in files if re.match(regex, x) ]

    if bad:
        sys.stdout.write(" [ FAIL ]\n" + 
            "Win32 binaries which are not binfiles:\n")
        for f in bad:
            print("  " + f)
    else:
        sys.stdout.write(" [ OK ]\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: lint_tlpdb.py <db> <package> <arch> [tltree]")
        print("\n  e.g. lint_tlpdb.py texscythe.db scheme-full" +
            " i386-linux /path/to/tree\n")
        sys.exit(1)

    (db, pkg, arch) = (sys.argv[1], sys.argv[2], sys.argv[3])
    print("Linting package '%s' from database '%s'" % (pkg, db))

    tltree = sys.argv[4] if len(sys.argv) == 5 else None

    # Base configuration, we will copy this per lint
    cfg = config.Config(
            dirs=False,
            plist=None, # means the set is returned
            sqldb=db,
            arch=arch,
            skip_missing_archpkgs=True,
            quiet=True,
            )

    print("\n%s\n" % cfg)

    # Here goes
    find_manuals_not_docfiles(cfg)
    find_windows_exes_not_binfiles(cfg)

    # Share the file list for these lints
    if tltree is not None:
        cfgp = copy.deepcopy(cfg)
        cfgp.inc_pkgspecs = [ pkg + ":run,src,doc" ]
        files = subset.compute_subset(cfgp)

        check_all_files_exist(files, tltree)
        find_manuals_in_wrong_path(files, tltree)

