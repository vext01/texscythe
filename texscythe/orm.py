from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os

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


def check_sqldb(cfg):
    create, update = False, False
    if not os.path.exists(cfg.sqldb):
        create = True
    elif os.path.getmtime(cfg.tlpdb) > os.path.getmtime(cfg.sqldb):
        update = True
    return create, update


def init_orm(cfg, force_create=False):
    """Set up ORM.
    SQL database is created and populated if non-existent or out of date.
    """

    # Check existence and mtime *before* opening connection.
    create, update = check_sqldb(cfg)
    if force_create:
        create = True

    engine = create_engine('sqlite:///%s' % (cfg.sqldb,))
    sess = sessionmaker(bind=engine)()

    if create:
        print("SQL database non-existent. Initialising...")
    elif update:
        print("SQL database out of date. Re-initialising...")

    if create or update:
        from tlpdbparser import initdb
        initdb(cfg, sess, engine)

    return sess
