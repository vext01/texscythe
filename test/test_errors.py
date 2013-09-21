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
            "tlpdb"             : os.path.join(DIRPATH, tlpdb + ".tlpdb"),
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
        pytest.raises(TeXParseError, 'self.parse_file("error_weird_line_postfix")')

    def test_files_not_indented(self):
        pytest.raises(TeXParseError, 'self.parse_file("error_files_not_indented")')

    def test_nonexistent_dep(self):
        self.parse_file("error_nonexistent_dep")
        pytest.raises(TeXSubsetError,
            'subset.compute_subset(self.config, ["rootpkg"], None, self.sess)')

    def test_unknwown_filetype(self):
        pytest.raises(TeXParseError, 'self.parse_file("error_unknown_filetype")')

    def test_nonexistent_dep(self):
        self.parse_file("basic") # should work
        # now ask for a class of file which is bogus, in this case 'fartfiles'
        pytest.raises(TeXSubsetError,
            'subset.compute_subset(self.config, ["rootpkg:fart"], None, self.sess)')

    def test_malformed_pkgspec(self):
        self.parse_file("basic") # should work
        pytest.raises(TeXSubsetError,
            'subset.compute_subset(self.config, ["rootpkg:doc:ouch"], None, self.sess)')
