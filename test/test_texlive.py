import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset, config

class Test_TeXLive(AbstractTest):
    """ Run some tests on a large texlive tlpdb """

    def setup_method(self, method):
        self.cfg = config.Config(
                sqldb=os.path.join(DIRPATH, "texlive2014.db"),
                plist=os.path.join(DIRPATH, "PLIST-texlive2014"),
                tlpdb=os.path.join(DIRPATH, "..", "texlive2014.tlpdb.gz"),
                dirs=False
                )

        super(Test_TeXLive, self).setup_method(method)

    @pytest.mark.slow
    def test_superficial(self):
        # numbers determined independently by grep
        assert self.sess.query(Package).count() == 5987
        assert self.sess.query(File).count() == 139123
