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
import os
import orm

from orm import Package, Dependency, File
from orm import DeclarativeBase


class TeXParseError(Exception):
    pass


class ParserState(object):
    """ Represents where abouts it the tlpdb we are """

    # for the want of a better word, we call these "filelevels"
    # (XXX: Use enum when moving to Python 3)
    TOPLEVEL = 0
    RUNFILES = 1
    DOCFILES = 2
    SRCFILES = 3
    BINFILES = 4

    # How many packages to parse before comitting to the DB.
    # Higher = faster, but more memory.
    COMMIT_THRESHOLD = 250

    def __init__(self, pkg, filelevel):
        self.pkg = pkg
        self.filelevel = filelevel
        self.num_pkgs_parsed = 0


def fieldname_and_data(s):
    try:
        space = s.index(" ")
    except:
        raise TeXParseError("Malformed line, no space: '%s'" % s)
    return (s[0:space], s[space + 1:])


def user_feedback(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def parse(sess, cfg):
    if not cfg.quiet:
        user_feedback("Parsing TLPDB...")

    if cfg.tlpdb.endswith(".gz"):
        import gzip
        with gzip.open(cfg.tlpdb, "r") as fh:
            parse_lines(sess, cfg, fh)
    else:
        with open(cfg.tlpdb, "r") as fh:
            parse_lines(sess, cfg, fh)

    if not cfg.quiet:
        print("\n")


def parse_lines(sess, cfg, fh):
    state = ParserState(None, ParserState.TOPLEVEL)
    for line in fh:
        parse_line(sess, cfg, line.rstrip("\n"), state)

    # Commit the last package we saw since we may
    # not have seen a newline to otherwise cause the commit.
    if state.pkg is not None:
        sess.add(state.pkg)


def parse_line(sess, cfg, line, state):
    if line.startswith(" "):
        parse_file_line(sess, cfg, line[1:], state)
    elif line.rstrip() == "":
        parse_end_package(sess, cfg, line, state)
    else:
        # If we get here, then the first word of the line is package metadata
        (field, data) = fieldname_and_data(line)
        funcname = ("parse_%s_data" % (field)).replace("-", "_")

        try:
            func = globals()[funcname]
        except KeyError:
            raise TeXParseError("Unknown package metadata '%s'. "
                                "Missing handler %s()" %
                                (field, funcname))

        func(sess, cfg, data, state)


filelevel_map = {
    ParserState.DOCFILES: "d",
    ParserState.SRCFILES: "s",
    ParserState.BINFILES: "b",
    ParserState.RUNFILES: "r",
}


def parse_file_line(sess, cfg, line, state):
    """ We get here when we see a file that is part of a package """
    assert state.pkg is not None and state.filelevel != ParserState.TOPLEVEL

    # Some file lines have junk on the end.
    # This slows us down a bit, but I would rather have this sanity check
    # in case later versions of tlpdb include stuff we should know about.
    fields = line.split(" ")
    if not (len(fields) == 1 or fields[1].startswith("details=")):
        raise TeXParseError("Weird file line: %d<<%s>> '%s'" %
                            (len(fields), fields, line, ))

    fl = File(pkgname=state.pkg.pkgname, filename=fields[0],
              filetype=filelevel_map[state.filelevel])
    sess.add(fl)


def parse_end_package(sess, cfg, data, state):
    """ Called when we hit the blank line inbetween packages """
    assert(state.pkg is not None)
    sess.add(state.pkg)

    state.num_pkgs_parsed += 1
    if state.num_pkgs_parsed % ParserState.COMMIT_THRESHOLD == 0:
        sess.commit()
        if not cfg.quiet:
            user_feedback("%s..." % state.num_pkgs_parsed)

    state.filelevel = ParserState.TOPLEVEL
    state.pkg = None


def parse_name_data(sess, cfg, data, state):
    """ This is executed when we hit the beginning of a new package """
    assert(state.pkg is None and state.filelevel == ParserState.TOPLEVEL)
    state.pkg = Package.skel(data)  # scaffold the package
    state.filelevel = ParserState.TOPLEVEL


def parse_shortdesc_data(sess, cfg, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)
    state.pkg.shortdesc = data


def parse_longdesc_data(sess, cfg, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)

    if state.pkg.longdesc is None:  # first longdesc line
        state.pkg.longdesc = ""

    state.pkg.longdesc += data


def parse_revision_data(sess, cfg, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)
    state.pkg.revision = int(data)


def parse_category_data(sess, cfg, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)


def parse_depend_data(sess, cfg, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)
    dep = Dependency(pkgname=state.pkg.pkgname, needs=data)
    sess.add(dep)


# Note that we assume that files information comes last in a package
def parse_runfiles_data(sess, cfg, data, state):
    assert(state.pkg is not None)
    state.filelevel = ParserState.RUNFILES


def parse_docfiles_data(sess, cfg, data, state):
    assert(state.pkg is not None)
    state.filelevel = ParserState.DOCFILES


def parse_srcfiles_data(sess, cfg, data, state):
    assert(state.pkg is not None)
    state.filelevel = ParserState.SRCFILES


def parse_binfiles_data(sess, cfg, data, state):
    assert(state.pkg is not None)
    state.filelevel = ParserState.BINFILES


def parse_catalogue_data(sess, cfg, data, state):
    pass


def parse_catalogue_ctan_data(sess, cfg, data, state):
    pass


def parse_catalogue_date_data(sess, cfg, data, state):
    pass


def parse_catalogue_license_data(sess, cfg, data, state):
    pass


def parse_catalogue_version_data(sess, cfg, data, state):
    pass


def parse_execute_data(sess, cfg, data, state):
    pass


def parse_postaction_data(sess, cfg, data, state):
    pass


def print_db_summary(sess):
    print(25 * "=")
    print("Database summary")
    print(25 * "=")
    print("Packages:     %8d" % sess.query(Package).count())
    print("Files:        %8d" % sess.query(File).count())
    print("Dependencies: %8d" % sess.query(Dependency).count())


def initdb(cfg, return_sess=False):
    # Since we will only ever use sqlite, we can do this
    if os.path.exists(cfg.sqldb):
        os.unlink(cfg.sqldb)

    # Set up ORM
    (sess, engine) = orm.init_orm(cfg.sqldb)
    DeclarativeBase.metadata.create_all(engine)

    # Populate db
    parse(sess, cfg)
    sess.commit()

    # Done
    if not cfg.quiet:
        print_db_summary(sess)

    if not return_sess:
        sess.close()
    else:
        return sess
