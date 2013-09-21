import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset, tlpdbparser

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
        # these shouldn't be needed as all tlpdbs have errors.
        # clean up incase a test does not expectedly fail
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

    @pytest.mark.xfail
    def test_weird_line_postfix(self):
        self.parse_file("weird_line_postfix")

    @pytest.mark.xfail
    def test_files_not_indented(self):
        self.parse_file("files_not_indented")
