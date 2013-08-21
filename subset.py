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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from orm import Package, Dependency, File

def compute_subset(include_pkgs, exclude_pkgs, outfilename="out.plist"):
    # argparse gives None if switch is absent
    if include_pkgs is None: include_pkgs = []
    if exclude_pkgs is None: exclude_pkgs = []

    # Set up ORM
    engine = create_engine('sqlite:///%s' % (config.SQLDBPATH))
    Session = sessionmaker(bind=engine)
    sess = Session()

    include_files = build_file_list(sess, include_pkgs)
    exclude_files = build_file_list(sess, exclude_pkgs)
    subset = include_files - exclude_files

    print("Subset has %d files" % len(subset))

    # XXX write away

def build_file_list(sess, packages):
    # we have to be careful how we do this to not explode the memory.
    # let's iteratively collect file lists from packages and accumulate them
    # in a set. This will remove duplicates as we go.
    files = set()
    for p in packages:
        files = files | build_file_list_pkg(sess, p)

    return files

def build_file_list_pkg(sess, pkgname):
    print("Build file list: %s" % pkgname)
    # look up package
    pkg = sess.query(Package).filter(Package.pkgname == pkgname).one()

    # add files
    files = set(pkg.files)

    # process deps and union with the above files.
    print(len(pkg.dependencies))
    for dep in pkg.dependencies:
        print("Dependency: %s" % dep)
        files |= build_file_list(sess, dep.pkgname)

    # return them
    return set(pkg.files)
