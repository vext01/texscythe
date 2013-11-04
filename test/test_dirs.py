import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset

class Test_Dirs(AbstractTest):

    def setup_method(self, method):
        self.config = {
            "sqldb"             : os.path.join(DIRPATH, "basic.db"),
            "plist"             : os.path.join(DIRPATH, "PLIST-basic"),
            "prefix_filenames"  : "",
            "tlpdb"             : os.path.join(DIRPATH, "basic.tlpdb"),
            "arch"              : None,
            "dirs"              : True,
            "regex"             : None,
        }

        super(Test_Dirs, self).setup_method(method)

    def test_dirs(self):
        subset.compute_subset(self.config, ["rootpkg"], None, self.sess)
        files = self._read_in_plist()

        expected = sorted([ "runfiles/runfile%d" % x for x in range(1, 4) ] + \
            [ "docfiles/docfile%d" % x for x in range(1, 3) ] + \
            [ "srcfiles/srcfile1" ] + [ "runfiles/", "docfiles/", "srcfiles/"])

        assert files == expected

    def test_dirs2(self):
        subset.compute_subset(self.config, ["rootpkg:run"], None, self.sess)
        files = self._read_in_plist()

        expected = sorted([ "runfiles/runfile%d" % x for x in range(1, 4) ] +
            [ "runfiles/"])

        assert files == expected

    def test_dirs3(self):
        subset.compute_subset(self.config, ["no_root_dirs_pkg:run"], None, self.sess)
        files = self._read_in_plist()

        expected = sorted([ "file1", "file2", "file3" ]) # no root dir entry
        assert files == expected

    def test_dirs4(self):
        subset.compute_subset(self.config, ["intermediate_dirs_pkg:run"], None, self.sess)
        files = self._read_in_plist()

        # should make intermediate dirs
        expected = sorted([ "a/", "a/b/", "a/b/c/", "a/b/c/file1" ])
        assert files == expected
