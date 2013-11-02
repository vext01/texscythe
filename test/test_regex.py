import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset

class Test_Regex(AbstractTest):

    def setup_method(self, method):
        self.config = {
            "sqldb"             : os.path.join(DIRPATH, "basic.db"),
            "plist"             : os.path.join(DIRPATH, "PLIST-basic"),
            "prefix_filenames"  : "",
            "tlpdb"             : os.path.join(DIRPATH, "basic.tlpdb"),
            "arch"              : None,
            "dirs"              : False
        }
        super(Test_Regex, self).setup_method(method)

    def test_regex(self):
        subset.compute_subset(self.config, ["rootpkg:run:.*runfile[13]$"], None, self.sess)
        files = self._read_in_plist()

        assert files == sorted(["runfiles/runfile1", "runfiles/runfile3"])

    def test_regex2(self):
        # check that finding nothing is possible
        subset.compute_subset(self.config, ["rootpkg::.*wontfindthis.*"], None, self.sess)
        files = self._read_in_plist()

        assert files == []

    def test_regex3(self):
        subset.compute_subset(self.config, ["rootpkg::.*(run|src)file[^3]$"], None, self.sess)
        files = self._read_in_plist()

        assert files == sorted([
            "runfiles/runfile1", "runfiles/runfile2",
            "srcfiles/srcfile1"
            ])

    def test_regex3(self):
        # check composing regex filters works
        subset.compute_subset(self.config,
                ["rootpkg::.*(run|src)file[^3]$", "rootpkg:doc:.*2$"], None, self.sess)
        files = self._read_in_plist()

        assert files == sorted([
            "runfiles/runfile1", "runfiles/runfile2",
            "docfiles/docfile2",
            "srcfiles/srcfile1"
            ])

    def test_regex4(self):
        # check regex as an exclude works
        subset.compute_subset(self.config,
                ["rootpkg::.*(run|src)file[^3]$"], ["rootpkg::.*2$"], self.sess)
        files = self._read_in_plist()

        assert files == sorted([ "runfiles/runfile1", "srcfiles/srcfile1" ])

    def test_regex5(self):
        # check that filtering >1 file type works
        subset.compute_subset(self.config, ["rootpkg:run,doc:.*[13]$"], None, self.sess)
        files = self._read_in_plist()

        assert files == sorted(["runfiles/runfile1", "runfiles/runfile3", "docfiles/docfile1"])
