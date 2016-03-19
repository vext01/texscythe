import pytest
import os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import config


class Test_TeXLive2014(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-texlive2014"),
                tlpdb=os.path.join(DIRPATH, "..", "texlive2014.tlpdb.gz"),
                dirs=False
                )

        super(Test_TeXLive2014, self).setup_method(method)

    @pytest.mark.slow
    def test_count0001(self):
        assert self.sess.query(Package).count() == 5987
        assert self.sess.query(File).count() == 139123


class Test_TeXLive2015(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-texlive2015"),
                tlpdb=os.path.join(DIRPATH, "..", "texlive2015.tlpdb.gz"),
                dirs=False
                )

        super(Test_TeXLive2015, self).setup_method(method)

    @pytest.mark.slow
    def test_count0001(self):
        assert self.sess.query(Package).count() == 5995
        assert self.sess.query(File).count() == 147335
