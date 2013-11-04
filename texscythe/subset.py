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

import sys, os.path, re

from orm import Package, Dependency, File, init_orm

class TeXSubsetError(Exception): pass

class FileSpec(object):
    def __init__(self, pkgname, filetypes, regex=None):
        self.pkgname = pkgname
        self.filetypes = filetypes
        self.regex = regex

    def __str__(self):
        return "FileSpec: pkgname='%s', filetypes=%s, regex=%s" % \
                (self.pkgname, self.filetypes, self.regex)

BLANK = 80 * " "
def feedback(action, message):
    sys.stderr.write("\r%s\r  %s: %s" % (BLANK, action, message))
    sys.stderr.flush()

def parse_subset_spec(spec):
    """ Parse subset specs. E.g.:
        scheme-tetex
        scheme-tetex:src
        scheme-tetex:src,run,doc
        scheme-tetex:src,run,doc:.*\.pdf

        returns a tuple, (name, list_of_filetypes)
    """

    elems = spec.split(":", 2)

    if len(elems) not in range(1, 4):
        raise TeXSubsetError("Bad filesepc: '%s'" % spec)

    # pad the elements up to 3 length and unpack
    elems = elems + [ "" for x in range(3 - len(elems)) ]

    (pkgname, filetypes, regex) = elems

    # parse file types
    if filetypes == "":
        filetypes = ["run", "src", "doc", "bin"] # all types
    else:
        filetypes = filetypes.split(",")
        for t in filetypes:
            if t not in ["run", "src", "doc", "bin"]:
                raise TeXSubsetError("Unknown file type: '%s'" % (t, ))

    # parse regex
    if regex == "":
        regex = None
    else:
        regex = re.compile(regex)

    return FileSpec(pkgname, filetypes, regex)

def compute_subset(config, include_pkgspecs, exclude_pkgspecs, sess = None):
    # argparse gives None if switch is absent
    if include_pkgspecs is None: include_pkgspecs = []
    if exclude_pkgspecs is None: exclude_pkgspecs = []

    # parse the pkgspecs
    include_specs = [ parse_subset_spec(s) for s in include_pkgspecs ]
    exclude_specs = [ parse_subset_spec(s) for s in exclude_pkgspecs ]

    if sess is None:
        (sess, engine) = init_orm(config["sqldb"])

    sys.stderr.write("Collecting include files:\n")
    include_files = build_file_list(config, sess, include_specs)
    sys.stderr.write("Collecting exclude files:\n")
    exclude_files = build_file_list(config, sess, exclude_specs)

    sys.stderr.write("Performing subtract... ")
    subset = include_files - exclude_files
    sys.stderr.write("Done\n")

    def get_required_dirs(path):
        dirs = []
        while path != "":
            path = os.path.dirname(path)
            if path != "": dirs.append(path + os.path.sep)
        return dirs

    if config["dirs"]:
        sys.stderr.write("Adding directory lines...")
        dirs = set()
        for line in subset: dirs |= set(get_required_dirs(line))

        subset |= dirs
        sys.stderr.write("Done\n")

    sys.stderr.write("Sorting... ")
    subset = sorted(subset)
    sys.stderr.write("Done\n")

    # Filter global regex.
    # Quicker to check once and duplicate code
    if config["regex"] is None: # no filter needed
        sys.stderr.write("Writing %d filenames to '%s'... " % 
            (len(subset), config["plist"]))
        with open(config["plist"], "w") as fh:
            for fl in subset:
                fh.write("%s%s\n" % (config["prefix_filenames"], fl))
    else:
        sys.stderr.write("Filtering %d filenames to '%s'... " % 
            (len(subset), config["plist"]))
        rgx = re.compile(config["regex"])
        with open(config["plist"], "w") as fh:
            for fl in subset:
                if rgx.match(fl): 
                    fh.write("%s%s\n" % (config["prefix_filenames"], fl))

    sys.stderr.write("Done\n")

def build_file_list(config, sess, filespecs):
    # we have to be careful how we do this to not explode the memory.
    # let's iteratively collect file lists from packages and accumulate them
    # in a set. This will remove duplicates as we go.

    files = set()
    for spec in filespecs:
        # Speed up file collection by noting which packages have already been
        # processed. Seems to make a big performance difference at the cost
        # of storing this large dict.
        seen_packages = {}

        new_files = build_file_list_pkg(config, sess, spec, seen_packages)

        rpattern = ":" + spec.regex.pattern if spec.regex is not None else ""
        feedback("Building file list", "done: %s:%s%s has %d files\n" % \
                (spec.pkgname, ",".join(spec.filetypes), rpattern, len(new_files)))
        files |= new_files

    return files

def build_file_list_pkg(config, sess, filespec, seen_packages):
    pkgname = filespec.pkgname
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
    for filetype in filespec.filetypes:
        # Note that in the DB filetype is just the first letter. If in the
        # future two filetypes of the same first letter arise, refactor.
        files |= set([ f.filename for f in \
                pkg.files.filter(File.filetype == filetype[0]).all() ])

    # filter based upon regex
    if filespec.regex is not None:
        files = set([ f for f in files if filespec.regex.match(f) ])

    # Process deps and union with the above files.
    # Pass down a new FileSpec that inherits filetypes and regex from the
    # current filespec.
    for dep in pkg.dependencies:
        files |= build_file_list_pkg(config, sess,
                FileSpec(dep.needs, filespec.filetypes, filespec.regex),
                seen_packages)

    # return them
    return files
