import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset, tlpdbparser, config
from texscythe.subset import TeXSubsetError
from texscythe.tlpdbparser import TeXParseError

class Test_Errors(object):
    """ Test a bunch of parser errors """

    def parse_file(self, tlpdb):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-errors"),
                tlpdb=os.path.join(DIRPATH, tlpdb + ".tlpdb"),
                arch="amd64-linux",
                dirs=False
                )
        self.sess = tlpdbparser.initdb(self.cfg, return_sess=True)

    def setup_method(self, method):
        self.cfg = None

    def teardown_method(self, method):
        if self.cfg is not None:
            try:
                os.unlink(self.cfg.sqldb)
            except OSError:
                pass

            try:
                os.unlink(self.cfg.plist)
            except OSError:
                pass

        try:
            self.sess.close()
        except:
            pass

    def test_weird_line_postfix(self):
        pytest.raises(TeXParseError, 'self.parse_file("error_weird_line_postfix")')

    def test_files_not_indented(self):
        pytest.raises(TeXParseError, 'self.parse_file("error_files_not_indented")')

    def test_nonexistent_dep(self):
        self.parse_file("error_nonexistent_dep")
        self.cfg.inc_pkgspecs = ["rootpkg"]
        pytest.raises(TeXSubsetError,
            'subset.compute_subset(self.cfg, self.sess)')

    def test_unknwown_filetype(self):
        pytest.raises(TeXParseError, 'self.parse_file("error_unknown_filetype")')

    def test_bad_filetype_dep(self):
        self.parse_file("basic") # should work
        # now ask for a class of file which is bogus, in this case 'fartfiles'
        self.cfg.inc_pkgspecs = ["rootpkg:fart"]
        pytest.raises(TeXSubsetError,
            'subset.compute_subset(self.cfg, self.sess)')

    def test_config_fields(self):
        # the config instance namespace is protected.
        c = config.Config("unused.tlpdb")
        pytest.raises(config.ConfigError, "c.bad_field = 'oh no!'")

    def test_missing_archpkg(self):
        self.parse_file("error_missing_archpkg")
        self.cfg.inc_pkgspecs = ["rootpkg"]
        pytest.raises(TeXSubsetError,
            'subset.compute_subset(self.cfg, self.sess)')
