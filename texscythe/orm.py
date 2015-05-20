from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class Package(DeclarativeBase):
    __tablename__ = "packages"
    # It may not be good relational database design to use a name as a primary
    # key, but it does mean that we only need a single pass over the tlpdb.
    # This is because we immediately know the primary key of dependencies.
    pkgname = Column(String, primary_key=True)
    revision = Column(Integer)
    shortdesc = Column(String)
    longdesc = Column(String)

    # XXX Categories
    # XXX catalogue-*

    @staticmethod
    def skel(pkgname):
        return Package(pkgname=pkgname)  # fill in the rest as we find it


class Dependency(DeclarativeBase):
    __tablename__ = "dependencies"
    id = Column(Integer, primary_key=True)
    pkgname = Column(String, ForeignKey("packages.pkgname"))
    needs = Column(String)

    package = relationship("Package", backref=backref("dependencies"))

    def __str__(self):
        return "Dependency: %s needs %s" % (self.pkgname, self.needs)


class File(DeclarativeBase):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    pkgname = Column(String, ForeignKey("packages.pkgname"))
    filename = Column(String)
    filetype = Column(String)  # [r]unfile/[s]rcfile/[d]ocfile/[b]infile

    package = relationship("Package", backref=backref("files", lazy='dynamic'))


def init_orm(tlpdb_path):
    # Set up ORM
    engine = create_engine('sqlite:///%s' % (tlpdb_path,))
    Session = sessionmaker(bind=engine)
    return (Session(), engine)
