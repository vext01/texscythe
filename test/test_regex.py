import os.path
from helper import AbstractTest, DIRPATH

from texscythe import subset, config


class Test_Regex(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-basic"),
                tlpdb=os.path.join(DIRPATH, "basic.tlpdb"),
                dirs=False
                )
        super(Test_Regex, self).setup_method(method)

    def test_regex(self):
        self.set_specs(["rootpkg:run:.*runfile[13]$"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == sorted(["runfiles/runfile1", "runfiles/runfile3"])

    def test_regex2(self):
        # check that finding nothing is possible
        self.set_specs(["rootpkg::.*wontfindthis.*"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == []

    def test_regex3(self):
        self.set_specs(["rootpkg::.*(run|src)file[^3]$"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == sorted([
            "runfiles/runfile1", "runfiles/runfile2",
            "srcfiles/srcfile1"
            ])

    def test_regex4(self):
        # check composing regex filters works
        self.set_specs(["rootpkg::.*(run|src)file[^3]$", "rootpkg:doc:.*2$"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == sorted([
            "runfiles/runfile1", "runfiles/runfile2",
            "docfiles/docfile2",
            "srcfiles/srcfile1"
            ])

    def test_regex5(self):
        # check regex as an exclude works
        self.set_specs(["rootpkg::.*(run|src)file[^3]$"], ["rootpkg::.*2$"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == sorted(["runfiles/runfile1", "srcfiles/srcfile1"])

    def test_regex6(self):
        # check that filtering >1 file type works
        self.set_specs(["rootpkg:run,doc:.*[13]$"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == sorted(["runfiles/runfile1", "runfiles/runfile3",
                                "docfiles/docfile1"])


class Test_GlobalRegex(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-basic"),
                tlpdb=os.path.join(DIRPATH, "basic.tlpdb"),
                dirs=False,
                regex=".*runfile[13]$"
                )
        super(Test_GlobalRegex, self).setup_method(method)

    def test_regex(self):
        self.set_specs(["rootpkg:run"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == sorted(["runfiles/runfile1", "runfiles/runfile3"])
