import os.path
from helper import AbstractTest, DIRPATH

from texscythe import subset, config


class Test_Dirs(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
            plist=os.path.join(DIRPATH, "PLIST-basic"),
            tlpdb=os.path.join(DIRPATH, "basic.tlpdb"),
            )

        super(Test_Dirs, self).setup_method(method)

    def test_dirs(self):
        self.set_specs(["rootpkg"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        expected = sorted(
            ["runfiles/runfile%d" % x for x in range(1, 4)] +
            ["docfiles/docfile%d" % x for x in range(1, 3)] +
            ["srcfiles/srcfile1"] + ["runfiles/", "docfiles/", "srcfiles/"]
        )

        assert files == expected

    def test_dirs2(self):
        self.set_specs(["rootpkg:run"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        expected = sorted(
            ["runfiles/runfile%d" % x for x in range(1, 4)] +
            ["runfiles/"]
        )

        assert files == expected

    def test_dirs3(self):
        self.set_specs(["no_root_dirs_pkg:run"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        expected = sorted(["file1", "file2", "file3"])  # no root dir entry
        assert files == expected

    def test_dirs4(self):
        self.set_specs(["intermediate_dirs_pkg:run"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        # should make intermediate dirs
        expected = sorted(["a/", "a/b/", "a/b/c/", "a/b/c/file1"])
        assert files == expected
