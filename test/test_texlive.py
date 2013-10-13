import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset

class Test_TeXLive(AbstractTest):
    """ Run some tests on a large texlive tlpdb """

    def setup_method(self, method):
        self.config = {
            "sqldb"             : os.path.join(DIRPATH, "texlive2013.db"),
            "plist"             : os.path.join(DIRPATH, "PLIST-texlive2013"),
            "prefix_filenames"  : "",
            "tlpdb"             : os.path.join(DIRPATH, "..", "texlive2013.tlpdb.gz"),
            "arch"              : None,
            "dirs"              : False
        }

        super(Test_TeXLive, self).setup_method(method)

    @pytest.mark.slow
    def test_superficial(self):
        # numbers determined independently by grep
        assert self.sess.query(Package).count() == 5599
        assert self.sess.query(File).count() == 127356
