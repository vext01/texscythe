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

import sys

import config
from orm import Package, Dependency, File, init_orm

BLANK = 80 * " "
def feedback(action, message):
    sys.stderr.write("\r%s\r  %s: %s" % (BLANK, action, message))
    sys.stderr.flush()

def compute_subset(include_pkgs, exclude_pkgs, outfilename="out.plist"):
    # argparse gives None if switch is absent
    if include_pkgs is None: include_pkgs = []
    if exclude_pkgs is None: exclude_pkgs = []

    (sess, engine) = init_orm()

    sys.stderr.write("Collecting include files:\n")
    include_files = build_file_list(sess, include_pkgs)
    sys.stderr.write("Collecting exclude files:\n")
    exclude_files = build_file_list(sess, exclude_pkgs)

    sys.stderr.write("Performing subtract... ")
    subset = include_files - exclude_files
    sys.stderr.write("Done\n")

    sys.stderr.write("Sorting... ")
    subset = sorted(subset)
    sys.stderr.write("Done\n")

    sys.stderr.write("Writing %d filenames to '%s'... " % (len(subset), config.PLISTOUTPATH))

    with open(config.PLISTOUTPATH, "w") as fh:
        for fl in subset: fh.write(fl + "\n")

    sys.stderr.write("Done\n")

def build_file_list(sess, packages):
    # we have to be careful how we do this to not explode the memory.
    # let's iteratively collect file lists from packages and accumulate them
    # in a set. This will remove duplicates as we go.
    files = set()
    for pkgname in packages:
        new_files = build_file_list_pkg(sess, pkgname)
        feedback("Building file list", "done: %s has %d files\n" % (pkgname, len(new_files)))
        files |= new_files

    return files

def build_file_list_pkg(sess, pkgname):
    feedback("Building file list", pkgname)
    if "ARCH" in pkgname: # XXX make configurable
        return set()

    # look up package
    pkg = sess.query(Package).filter(Package.pkgname == pkgname).one()

    # add files
    files = set([ f.filename for f in set(pkg.files) ])

    # process deps and union with the above files.
    for dep in pkg.dependencies:
        files |= build_file_list_pkg(sess, dep.needs)

    # return them
    return files
