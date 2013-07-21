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

def parse(sess, filename):
    with open(filename, "r") as fh: parse_lines(sess, fh)

def parse_lines(sess, fh):
    for l in fh: parse_line(sess, l)

def parse_line(sess, line):
    pass

if __name__ == "__main__":
    engine = create_engine('sqlite:///tmp/texscythe.db', echo=True)
    sess = sessionmaker(bind=engine)
    parse(sess, "texlive.tlpdb")
