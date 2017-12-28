import sys
import os

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
    except ValueError:
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


def empty_parse_handler(sess, cfg, data, state):
    pass


parse_catalogue_data = empty_parse_handler
parse_catalogue_ctan_data = empty_parse_handler
parse_catalogue_date_data = empty_parse_handler
parse_catalogue_license_data = empty_parse_handler
parse_catalogue_version_data = empty_parse_handler
parse_execute_data = empty_parse_handler
parse_postaction_data = empty_parse_handler
parse_catalogue_topics_data = empty_parse_handler
parse_catalogue_also_data = empty_parse_handler


def print_db_summary(sess):
    print(25 * "=")
    print("Database summary")
    print(25 * "=")
    print("Packages:     %8d" % sess.query(Package).count())
    print("Files:        %8d" % sess.query(File).count())
    print("Dependencies: %8d" % sess.query(Dependency).count())


def initdb(cfg, sess, engine):
    # Since we will only ever use sqlite, we can do this
    if os.path.exists(cfg.sqldb):
        os.unlink(cfg.sqldb)

    DeclarativeBase.metadata.create_all(engine)

    # Populate db
    parse(sess, cfg)
    sess.commit()

    # Set the mtime of the database to match the tlpdb. Used to detect if the
    # database is out of date. The resolution set by os.utime seems to less
    # than os.path.mtime. To make the times match we set the mtime of *both*
    # the tlpdb *and* the sqldb.
    tlpdb_time = os.path.getmtime(cfg.tlpdb)
    os.utime(cfg.sqldb, (tlpdb_time, tlpdb_time))
    os.utime(cfg.tlpdb, (tlpdb_time, tlpdb_time))

    # Done
    if not cfg.quiet:
        print_db_summary(sess)
