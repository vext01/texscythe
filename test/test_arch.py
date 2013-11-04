import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset

class Test_BasicWithArch(AbstractTest):

    def setup_method(self, method):
        self.config = {
            "sqldb"             : os.path.join(DIRPATH, "basic_arch.db"),
            "plist"             : os.path.join(DIRPATH, "PLIST-basic_arch"),
            "prefix_filenames"  : "",
            "tlpdb"             : os.path.join(DIRPATH, "basic.tlpdb"),
            "arch"              : "amd64-linux",
            "dirs"              : False,
            "regex"             : None,
        }

        super(Test_BasicWithArch, self).setup_method(method)

    def test_plist_binfiles(self):
        subset.compute_subset(self.config, ["rootpkg:bin"], None, self.sess)
        files = self._read_in_plist()

        # Since we *did* supply an arch we should see binfiles here
        assert files == ['binfiles/binfile1']

    def test_explicit_everything(self):
        subset.compute_subset(self.config, ["rootpkg"], None, self.sess)
        files1 = self._read_in_plist()

        subset.compute_subset(self.config, ["rootpkg:run,doc,src,bin"], None, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2

    def test_multiple_includes(self):
        subset.compute_subset(self.config, ["rootpkg:run", "rootpkg:bin"], None, self.sess)
        files1 = self._read_in_plist()

        subset.compute_subset(self.config, ["rootpkg:run,bin"], None, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2

    def test_multiple_includes2(self):
        subset.compute_subset(self.config, ["rootpkg:run", "rootpkg:bin", "rootpkg:src", "rootpkg:doc"], None, self.sess)
        files1 = self._read_in_plist()

        subset.compute_subset(self.config, ["rootpkg"], None, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2

    def test_multiple_excludes(self):
        subset.compute_subset(self.config, ["rootpkg"], ["rootpkg:src", "rootpkg:doc", "rootpkg:bin"], self.sess)
        files1 = self._read_in_plist()

        subset.compute_subset(self.config, ["rootpkg:run"], None, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2
