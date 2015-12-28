class ConfigError(Exception):
    pass


class Config(object):
    """ Wrapper for command line configuration (with defaults) """

    __fields = ["sqldb", "plist", "prefix_filenames", "tlpdb",
                "arch", "dirs", "regex", "inc_pkgspecs", "exc_pkgspecs",
                "quiet", "skip_missing_archpkgs"]

    def __init__(self, tlpdb,
                 plist="PLIST",
                 prefix_filenames="",
                 arch=None,
                 dirs=True,
                 regex=None,
                 inc_pkgspecs=[],
                 exc_pkgspecs=[],
                 quiet=False,
                 skip_missing_archpkgs=False):
        self.sqldb = tlpdb + ".db"
        self.plist = plist
        self.prefix_filenames = prefix_filenames
        self.tlpdb = tlpdb
        self.arch = arch
        self.dirs = dirs
        self.regex = regex
        self.inc_pkgspecs = inc_pkgspecs
        self.exc_pkgspecs = exc_pkgspecs
        self.quiet = quiet
        self.skip_missing_archpkgs = skip_missing_archpkgs

    def __str__(self):
        s = ["Configuration:"]
        s = ["  %s: %s" % (x, self.__dict__[x]) for x in Config.__fields]
        return "\n".join(s)

    def __setattr__(self, name, value):
        # Try to avoid mistyping some of the config names.
        # I know this isn't very pythonic.
        if name not in Config.__fields:
            raise ConfigError("Mistyped a configuration field: '%s'" % name)

        self.__dict__[name] = value
