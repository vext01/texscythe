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

import sys, os, os.path

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# ---/// ORM Mappings ///----------------------------------------------

# XXX Categories
# XXX catalogue-*

Base = declarative_base()

class Package(Base):
    __tablename__ = "packages"
    # It may not be good relational database design to use a name as a primary
    # key, but it does mean that we only need a single pass over the tlpdb.
    # This is because we immediately know the primary key of dependencies.
    pkgname = Column(String, primary_key=True)
    revision = Column(Integer)
    shortdesc = Column(String)
    longdesc = Column(String)

    @staticmethod
    def skel(pkgname): return Package(pkgname=pkgname) # fill in the rest as we find it

class Dependency(Base):
    __tablename__ = "dependencies"
    id = Column(Integer, primary_key=True)
    pkgname = Column(String)
    needs = Column(String, ForeignKey("packages.pkgname"))

    package = relationship("Package", backref=backref("dependencies"))

    def __str__(self):
        return "Dependency: %s needs %s" % (self.pkgname, self.needs)

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    pkgname = Column(String, ForeignKey("packages.pkgname"))
    filename = Column(String)
    filetype = Column(String) # [r]unfile/[s]rcfile/[d]ocfile/[b]infile

    package = relationship("Package", backref=backref("files"))

# ---/// Parsing Gunk ///----------------------------------------------

class TeXParseError(Exception): pass

class ParserState(object):
    """ Represents where abouts it the tlpdb we are """

    # for the want of a better word, we call these "filelevels"
    TOPLEVEL = 0
    RUNFILES = 1
    DOCFILES = 2
    SRCFILES = 3
    BINFILES = 4

    def __init__(self, pkg, filelevel):
        self.pkg = pkg
        self.filelevel = filelevel

def fieldname_and_data(s):
    space = s.index(" ")
    return (s[0:space], s[space + 1:])

def parse(sess, filename):
    print("Parsing tlpdb...")
    with open(filename, "r") as fh: parse_lines(sess, fh)

def parse_lines(sess, fh):
    state = ParserState(None, ParserState.TOPLEVEL)
    for line in fh:
        state = parse_line(sess, line.rstrip(), state)

def parse_line(sess, line, state):
    if line.startswith(" "):
        return parse_file_line(sess, line[1:], state)
    elif line == "":
        return parse_end_package(sess, line, state)

    # If we get here, then the first word of the line is package metadata
    (field, data) = fieldname_and_data(line)
    funcname = ("parse_%s_data" % (field)).replace("-", "_")

    try:
        func = globals()[funcname]
    except KeyError:
        raise TeXParseError(
                "Unknown package metadata '%s'. Missing handler %s()" % \
                (field, funcname))

    return func(sess, data, state)

filelevel_map = { \
    ParserState.DOCFILES : "d",
    ParserState.SRCFILES : "s",
    ParserState.BINFILES : "b",
    ParserState.RUNFILES : "r",
    }
def parse_file_line(sess, line, state):
    """ We get here when we see a file that is part of a package """
    assert state.pkg is not None and state.filelevel != ParserState.TOPLEVEL
    fl = File(pkgname=state.pkg.pkgname, filename=line, filetype=filelevel_map[state.filelevel])
    sess.add(fl)
    return state

def parse_end_package(sess, data, state):
    """ Called when we hit the blank line inbetween packages """
    assert(state.pkg is not None)
    sess.add(state.pkg)
    sess.commit()
    return ParserState(None, ParserState.TOPLEVEL)

def parse_name_data(sess, data, state):
    """ This is executed when we hit the beginning of a new package """
    assert(state.pkg is None and state.filelevel == ParserState.TOPLEVEL)
    return ParserState(Package.skel(data), ParserState.TOPLEVEL)

def parse_shortdesc_data(sess, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)
    state.pkg.shortdesc = data
    return state

def parse_longdesc_data(sess, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)

    if state.pkg.longdesc is None: # first longdesc line
        state.pkg.longdesc = ""

    state.pkg.longdesc += data
    return state

def parse_revision_data(sess, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)
    state.pkg.revision = int(data)
    return state

def parse_category_data(sess, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)
    return state

def parse_depend_data(sess, data, state):
    assert(state.pkg is not None and state.filelevel == ParserState.TOPLEVEL)
    dep = Dependency(pkgname=state.pkg.pkgname, needs=data)
    sess.add(dep)
    return state

# Note that we assume that files information comes last in a package
def parse_runfiles_data(sess, data, state):
    assert(state.pkg is not None)
    return ParserState(state.pkg, ParserState.RUNFILES)

def parse_docfiles_data(sess, data, state):
    assert(state.pkg is not None)
    return ParserState(state.pkg, ParserState.DOCFILES)

def parse_srcfiles_data(sess, data, state):
    assert(state.pkg is not None)
    return ParserState(state.pkg, ParserState.SRCFILES)

def parse_binfiles_data(sess, data, state):
    assert(state.pkg is not None)
    return ParserState(state.pkg, ParserState.BINFILES)

def parse_catalogue_data(sess, data, state):
    return state

def parse_catalogue_ctan_data(sess, data, state):
    return state

def parse_catalogue_date_data(sess, data, state):
    return state

def parse_catalogue_license_data(sess, data, state):
    return state

def parse_catalogue_version_data(sess, data, state):
    return state

def parse_execute_data(sess, data, state):
    return state

def parse_postaction_data(sess, data, state):
    return state

def print_db_summary(sess):
    print(25 * "=")
    print("Database summary")
    print(25 * "=")
    print("Packages:     %8d" % sess.query(Package).count())
    print("Files:        %8d" % sess.query(File).count())
    print("Dependencies: %8d" % sess.query(Dependency).count())

if __name__ == "__main__":
    DBPATH = "texscythe.db"

    # Since we will only ever use sqlite, we can do this
    if os.path.exists(DBPATH): os.unlink(DBPATH)

    # Set up ORM
    engine = create_engine('sqlite:///%s' % (DBPATH))
    Session = sessionmaker(bind=engine)
    sess = Session()
    Base.metadata.create_all(engine) 

    # Populate db
    parse(sess, "texlive.tlpdb")
    print_db_summary(sess)
    sess.close()

