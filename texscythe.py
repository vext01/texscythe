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

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref

# ---/// ORM Mappings ///----------------------------------------------

class Package(object):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    revision = Column(Integer)
    shortdesc = Column(String)
    longdesc = Column(String)

class Dependency(object):
    __tablename__ = "dependencies"
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("packages.id"))

    package = relationship("Package", backref=backref("dependencies"))

class File(object):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("packages.id"))
    filename = Column(String)
    filetype = Column(String) # [r]unfile/[s]rcfile/[d]ocfile

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

def parse(sess, filename):
    with open(filename, "r") as fh: parse_lines(sess, fh)

def parse_lines(sess, fh):
    state = ParserState(None, ParserState.TOPLEVEL)
    for line in fh:
        state = parse_line(sess, line, state)

def parse_line(sess, line, state):
    if line.startswith(" "):
        return parse_file_line(sess, line, state)
    elif line.strip() == "":
        return parse_end_package(sess, line, state)

    # If we get here, then the first word of the line is package metadata
    firstword = line.split(" ")[0]
    funcname = ("parse_%s_line" % (firstword)).replace("-", "_")

    try:
        func = globals()[funcname]
    except KeyError:
        raise TeXParseError(
                "Unknown package metadata '%s'. Missing handler %s()" % \
                (firstword, funcname))

    func(sess, line, state)

def parse_file_line(sess, line, state):
    pass

def parse_end_package(sess, line, state):
    pass

def parse_name_line(sess, line, state):
    pass

def parse_shortdesc_line(sess, line, state):
    pass

def parse_longdesc_line(sess, line, state):
    pass

def parse_revision_line(sess, line, state):
    pass

def parse_category_line(sess, line, state):
    pass

def parse_depend_line(sess, line, state):
    pass

def parse_runfiles_line(sess, line, state):
    pass

def parse_docfiles_line(sess, line, state):
    pass

def parse_srcfiles_line(sess, line, state):
    pass

def parse_binfiles_line(sess, line, state):
    pass

def parse_catalogue_line(sess, line, state):
    pass

def parse_catalogue_ctan_line(sess, line, state):
    pass

def parse_catalogue_date_line(sess, line, state):
    pass

def parse_catalogue_license_line(sess, line, state):
    pass

def parse_catalogue_version_line(sess, line, state):
    pass

def parse_execute_line(sess, line, state):
    pass

def parse_postaction_line(sess, line, state):
    pass

if __name__ == "__main__":
    engine = create_engine('sqlite:///tmp/texscythe.db', echo=True)
    sess = sessionmaker(bind=engine)
    parse(sess, "texlive.tlpdb")
