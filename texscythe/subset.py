import sys
import os.path
import re

from orm import Package, File
from sqlalchemy.orm.exc import NoResultFound

BLANK = 80 * " "


class TeXSubsetError(Exception):
    pass


class FileSpec(object):
    def __init__(self, pkgname, filetypes, regex=None, no_depends=False):
        self.pkgname = pkgname
        self.filetypes = filetypes
        self.regex = regex
        self.no_depends = no_depends

    def __str__(self):
        return ("FileSpec: pkgname='%s', filetypes=%s, "
                "regex=%s,no_depends=%s" %
                (self.pkgname, self.filetypes, self.regex, self.no_depends))


def feedback(action, message):
    sys.stderr.write("\r%s\r  %s: %s" % (BLANK, action, message))
    sys.stderr.flush()


def parse_subset_spec(spec):
    """ Parse subset specs. E.g.:
        scheme-tetex
        scheme-tetex:src
        !scheme-tetex:src
        scheme-tetex:src,run,doc
        scheme-tetex:src,run,doc:.*\.pdf
    """

    elems = spec.split(":", 2)

    if len(elems) not in range(1, 4):
        raise TeXSubsetError("Bad filesepc: '%s'" % spec)

    # pad the elements up to 3 length and unpack
    elems = elems + ["" for x in range(3 - len(elems))]

    (pkgname, filetypes, regex) = elems

    # if the package name is prefixed with a bang, it means, don't
    # collect dependencies.
    if pkgname.startswith("!"):
        pkgname = pkgname[1:]
        no_depends = True
    else:
        no_depends = False

    # parse file types
    if filetypes == "":
        filetypes = ["run", "src", "doc", "bin"]  # all types
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

    return FileSpec(pkgname, filetypes, regex, no_depends)


# Adds directory entries for a file
def dir_entries(path, exclude=[]):
    dirs = []
    while path != "":
        path = os.path.dirname(path)
        if path != "" and path not in exclude:
            dirs.append(path + os.path.sep)
    return dirs


def compute_subset(cfg, sess):
    # parse the pkgspecs
    include_specs = [parse_subset_spec(s) for s in cfg.inc_pkgspecs]
    exclude_specs = [parse_subset_spec(s) for s in cfg.exc_pkgspecs]

    if not cfg.quiet:
        sys.stderr.write("Collecting include files:\n")
    include_files = build_file_list(cfg, sess, include_specs)

    if not cfg.quiet:
        sys.stderr.write("Collecting exclude files:\n")
    exclude_files = build_file_list(cfg, sess, exclude_specs)

    if not cfg.quiet:
        sys.stderr.write("Performing subtract... ")
    subset = include_files - exclude_files
    if not cfg.quiet:
        sys.stderr.write("Done\n")

    if cfg.dirs:
        if not cfg.quiet:
            sys.stderr.write("Adding directory lines...")
        dirs = set()
        for line in subset:
            dirs |= set(dir_entries(line))

        subset |= dirs
        if not cfg.quiet:
            sys.stderr.write("Done\n")

    if not cfg.quiet:
        sys.stderr.write("Sorting... ")
    subset = sorted(subset)
    if not cfg.quiet:
        sys.stderr.write("Done\n")

    # Apply global regex if there is one
    if cfg.regex is not None:
        if not cfg.quiet:
            sys.stderr.write("Applying global regex...")
        rgx = re.compile(cfg.regex)
        subset = set([x for x in subset if rgx.match(x)])
        if not cfg.quiet:
            sys.stderr.write("Done\n")

    if cfg.plist is not None:
        # Write out to file
        if not cfg.quiet:
            sys.stderr.write("Writing file list to '%s'..." % cfg.plist)
        with open(cfg.plist, "w") as fh:
            for fl in sorted(subset):
                fh.write("%s%s\n" % (cfg.prefix_filenames, fl))
        if not cfg.quiet:
            sys.stderr.write("Done\n")
    else:
        return sorted(["%s%s" % (cfg.prefix_filenames, f) for f in subset])


def build_file_list(cfg, sess, filespecs):
    # we have to be careful how we do this to not explode the memory.
    # let's iteratively collect file lists from packages and accumulate them
    # in a set. This will remove duplicates as we go.

    files = set()
    for spec in filespecs:
        # Speed up file collection by noting which packages have
        # already been processed. Seems to make a big performance
        # difference at the cost # of storing this large dict.
        seen_packages = {}

        new_files = build_file_list_pkg(cfg, sess, spec, seen_packages)

        rpattern = ":" + spec.regex.pattern \
            if spec.regex is not None else ""

        if not cfg.quiet:
            feedback("Building file list",
                     "done: %s:%s%s has %d files\n" %
                     (spec.pkgname, ",".join(spec.filetypes),
                      rpattern, len(new_files)))
        files |= new_files

    return files


def build_file_list_pkg(cfg, sess, filespec, seen_packages):
    pkgname = filespec.pkgname
    if not cfg.quiet:
        feedback("Building file list", pkgname)

    archpkg = False
    if "ARCH" in pkgname:
        # If a cpu architecture was not sepcified, then binaries are ignored.
        if cfg.arch is None:
            return set()
        else:
            # substitute in arch name
            pkgname = pkgname.replace("ARCH", cfg.arch)
            archpkg = True

    try:
        seen_packages[pkgname]
        return set()  # already processed this pkg
    except KeyError:
        pass

    seen_packages[pkgname] = True

    # look up package
    try:
        pkg = sess.query(Package).filter(Package.pkgname == pkgname).one()
    except NoResultFound:
        if archpkg and cfg.skip_missing_archpkgs:
            return set()
        else:
            raise TeXSubsetError("Nonexistent TeX package: '%s'" % pkgname)

    # add files
    files = set()
    for filetype in filespec.filetypes:
        # Note that in the DB filetype is just the first letter. If in the
        # future two filetypes of the same first letter arise, refactor.
        files |= set([f.filename for f in
                      pkg.files.filter(File.filetype == filetype[0]).all()])

    # filter based upon regex
    if filespec.regex is not None:
        files = set([f for f in files if filespec.regex.match(f)])

    # Process deps and union with the above files.
    # Pass down a new FileSpec that inherits filetypes and regex from the
    # current filespec.
    if not filespec.no_depends:
        for dep in pkg.dependencies:
            files |= build_file_list_pkg(cfg, sess, FileSpec(
                dep.needs, filespec.filetypes, filespec.regex), seen_packages)
    # return them
    return files
