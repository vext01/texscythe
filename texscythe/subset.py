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

from orm import Package, Dependency, File, init_orm

class TeXSubsetError(Exception): pass

BLANK = 80 * " "
def feedback(action, message):
    sys.stderr.write("\r%s\r  %s: %s" % (BLANK, action, message))
    sys.stderr.flush()

def parse_subset_spec(spec):
    """ Parse subset specs. E.g.:
        scheme-tetex
        scheme-tetex:src
        scheme-tetex:src,run,doc

        returns a tuple, (name, list_of_filetypes)
    """

    elems = spec.split(":")
    if len(elems) == 1:
        return (elems[0], ["run", "src", "doc", "bin"])
    elif len(elems) == 2:
        filetypes = elems[1].split(",")
        for t in filetypes:
            if t == "": break # user passed "pkgname:"
            if t not in ["run", "src", "doc", "bin"]:
                raise TeXSubsetError("Unknown file type: '%s'" % (t, ))
        return (elems[0], filetypes)
    else:
        raise TeXSubsetError("Malformed pkgspec: '%s'" % (spec, ))

def compute_subset(config, include_pkgspecs, exclude_pkgspecs, sess = None):
    # argparse gives None if switch is absent
    if include_pkgspecs is None: include_pkgspecs = []
    if exclude_pkgspecs is None: exclude_pkgspecs = []

    # parse the pkgspecs
    include_tuples = [ parse_subset_spec(s) for s in include_pkgspecs ]
    exclude_tuples = [ parse_subset_spec(s) for s in exclude_pkgspecs ]

    if sess is None:
        (sess, engine) = init_orm(config["sqldb"])

    sys.stderr.write("Collecting include files:\n")
    include_files = build_file_list(config, sess, include_tuples)
    sys.stderr.write("Collecting exclude files:\n")
    exclude_files = build_file_list(config, sess, exclude_tuples)

    sys.stderr.write("Performing subtract... ")
    subset = include_files - exclude_files
    sys.stderr.write("Done\n")

    sys.stderr.write("Sorting... ")
    subset = sorted(subset)
    sys.stderr.write("Done\n")

    sys.stderr.write("Writing %d filenames to '%s'... " % (len(subset), config["plist"]))

    with open(config["plist"], "w") as fh:
        for fl in subset: fh.write("%s%s\n" % (config["prefix_filenames"], fl))

    sys.stderr.write("Done\n")

def build_file_list(config, sess, pkg_tuples):
    # we have to be careful how we do this to not explode the memory.
    # let's iteratively collect file lists from packages and accumulate them
    # in a set. This will remove duplicates as we go.

    files = set()
    for (pkgname, filetypes) in pkg_tuples:
        # Speed up file collection by noting which packages have already been
        # processed. Seems to make a big performance difference at the cost
        # of storing this large dict.
        seen_packages = {}

        new_files = build_file_list_pkg(config, sess, pkgname, filetypes, seen_packages)
        feedback("Building file list", "done: %s:%s has %d files\n" % \
                (pkgname, ",".join(filetypes), len(new_files)))
        files |= new_files

    return files

def build_file_list_pkg(config, sess, pkgname, filetypes, seen_packages):
    feedback("Building file list", pkgname)

    if "ARCH" in pkgname:
        # If a cpu architecture was not sepcified, then binaries are ignored.
        if config["arch"] is None:
            return set()
        else:
            # substitute in arch name
            pkgname = pkgname.replace("ARCH", config["arch"])

    try:
        seen_packages[pkgname]
        return set() # already processed this pkg
    except KeyError:
        pass

    seen_packages[pkgname] = True

    # look up package
    try:
        pkg = sess.query(Package).filter(Package.pkgname == pkgname).one()
    except:
        raise TeXSubsetError("Nonexistent TeX package: '%s'" % pkgname)

    # add files
    files = set()
    for filetype in filetypes:
        files |= set([ f.filename for f in \
                pkg.files.filter(File.filetype == filetype[0]).all() ])

    # process deps and union with the above files.
    for dep in pkg.dependencies:
        files |= build_file_list_pkg(config, sess, dep.needs, filetypes, seen_packages)

    # return them
    return files
