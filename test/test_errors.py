import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset, tlpdbparser
from texscythe.subset import TeXSubsetError
from texscythe.tlpdbparser import TeXParseError

class Test_Errors(object):
    """ Test a bunch of parser errors """

    def parse_file(self, tlpdb):
        self.config = {
            "sqldb"             : os.path.join(DIRPATH, "errors.db"),
            "plist"             : os.path.join(DIRPATH, "PLIST-errors"),
            "prefix_filenames"  : "",
            "tlpdb"             : "error_" + tlpdb + ".tlpdb",
            "arch"              : None,
        }
        self.sess = tlpdbparser.initdb(self.config, return_sess=True)

    def teardown_method(self, method):
        try:
            os.unlink(self.config["sqldb"])
        except:
            pass

        try:
            os.unlink(self.config["plist"])
        except:
            pass

        try:
            self.sess.close()
        except:
            pass

    def test_weird_line_postfix(self):
        pytest.raises(TeXParseError, 'self.parse_file("weird_line_postfix")')

    def test_files_not_indented(self):
        pytest.raises(TeXParseError, 'self.parse_file("files_not_indented")')

    def test_nonexistent_dep(self):
        self.parse_file("nonexistent_dep")
        pytest.raises(TeXSubsetError, 'subset.compute_subset(self.config, ["rootpkg"], None, self.sess)')
