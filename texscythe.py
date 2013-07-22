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

Base = declarative_base()

class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # XXX category = Column(String)
    revision = Column(Integer)
    shortdesc = Column(String)
    longdesc = Column(String)

    @staticmethod
    def skel(name): return Package(name=name) # fill in the rest as we find it

class Dependency(Base):
    __tablename__ = "dependencies"
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("packages.id"))

    package = relationship("Package", backref=backref("dependencies"))

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("packages.id"))
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
        return parse_file_line(sess, line, state)
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

def parse_file_line(sess, line, state):
    return state

def parse_end_package(sess, data, state):
    """ Called when we hit the blank line inbetween packages """
    assert(state.pkg is not None)
    sess.add(state.pkg)
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
    state.pkg.revision = int(data)
    return state

def parse_category_data(sess, data, state):
    return state

def parse_depend_data(sess, data, state):
    return state

def parse_runfiles_data(sess, data, state):
    return state

def parse_docfiles_data(sess, data, state):
    return state

def parse_srcfiles_data(sess, data, state):
    return state

def parse_binfiles_data(sess, data, state):
    return state

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
    sess.commit()
