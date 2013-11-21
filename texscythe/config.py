#!/usr/bin/env python2.7
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

class ConfigError(Exception): pass

class Config(object):
    """ Wrapper for command line configuration (with defaults) """

    __fields = ["sqldb", "plist", "prefix_filenames", "tlpdb", "arch", "dirs",
            "regex", "inc_pkgspecs", "exc_pkgspecs"]

    def __init__(self,
            sqldb="texscythe.db",
            plist="PLIST",
            prefix_filenames="",
            tlpdb="texlive.tlpdb",
            arch=None,
            dirs=True,
            regex=None,
            inc_pkgspecs=[],
            exc_pkgspecs=[],
            ):
        self.sqldb = sqldb
        self.plist = plist
        self.prefix_filenames = prefix_filenames
        self.tlpdb = tlpdb
        self.arch = arch
        self.dirs = dirs
        self.regex = regex
        self.inc_pkgspecs = inc_pkgspecs
        self.exc_pkgspecs = exc_pkgspecs

    def __str__(self):
        s = []
        s.append("Configuration:")
        s.append("  sqldb: %s" % self.sqldb)
        s.append("  plist: %s" % self.plist)
        s.append("  prefix_filenames: %s" % self.prefix_filenames)
        s.append("  tlpdb: %s" % self.tlpdb)
        s.append("  arch: %s" % self.arch)
        s.append("  dirs: %s" % self.dirs)
        s.append("  regex: %s" % self.regex)
        s.append("  inc_pkgspecs: %s" % self.inc_pkgspecs)
        s.append("  exc_pkgspecs: %s" % self.exc_pkgspecs)
        return "\n".join(s)

    def __setattr__(self, name, value):
        # Try to avoid mistyping some of the config names.
        # I know this isn't very pythonic.
        if name not in Config.__fields:
            raise ConfigError("You mistyped a configuration field: '%s'" % name)

        self.__dict__[name] = value
