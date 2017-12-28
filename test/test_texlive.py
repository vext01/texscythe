import pytest
import os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import config


class BaseTestTexLive(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-texlive%s" % self.VERSION),
                tlpdb=os.path.join(DIRPATH, "..",
                                   "texlive%s.tlpdb.gz" % self.VERSION),
                dirs=False)
        super(BaseTestTexLive, self).setup_method(method)


class Test_TeXLive2015(BaseTestTexLive):
    VERSION = 2015

    @pytest.mark.slow
    def test_count0001(self):
        assert self.sess.query(Package).count() == 5995
        assert self.sess.query(File).count() == 147335


class Test_TeXLive2016(BaseTestTexLive):
    VERSION = 2016

    @pytest.mark.slow
    def test_count0001(self):
        assert self.sess.query(Package).count() == 6091
        assert self.sess.query(File).count() == 153745


class Test_TeXLive2017(BaseTestTexLive):
    VERSION = 2017

    @pytest.mark.slow
    def test_count0001(self):
        assert self.sess.query(Package).count() == 6709
        assert self.sess.query(File).count() == 161437
