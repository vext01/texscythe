import os.path
from helper import AbstractTest, DIRPATH

from texscythe import subset, config


class Test_BasicWithArch(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-basic_arch"),
                tlpdb=os.path.join(DIRPATH, "basic.tlpdb"),
                arch="amd64-linux",
                dirs=False
                )

        super(Test_BasicWithArch, self).setup_method(method)

    def test_plist_binfiles(self):
        self.set_specs(["rootpkg:bin"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        # Since we *did* supply an arch we should see binfiles here
        assert files == ['binfiles/binfile1']

    def test_explicit_everything(self):
        self.set_specs(["rootpkg"])
        subset.compute_subset(self.cfg, self.sess)
        files1 = self._read_in_plist()

        self.set_specs(["rootpkg:run,doc,src,bin"])
        subset.compute_subset(self.cfg, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2

    def test_multiple_includes(self):
        self.set_specs(["rootpkg:run", "rootpkg:bin"])
        subset.compute_subset(self.cfg, self.sess)
        files1 = self._read_in_plist()

        self.set_specs(["rootpkg:run,bin"])
        subset.compute_subset(self.cfg, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2

    def test_multiple_includes2(self):
        self.set_specs(["rootpkg:run", "rootpkg:bin",
                        "rootpkg:src", "rootpkg:doc"])
        subset.compute_subset(self.cfg, self.sess)
        files1 = self._read_in_plist()

        self.set_specs(["rootpkg"])
        subset.compute_subset(self.cfg, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2

    def test_multiple_excludes(self):
        self.set_specs(["rootpkg"], ["rootpkg:src", "rootpkg:doc",
                                     "rootpkg:bin"])
        subset.compute_subset(self.cfg, self.sess)
        files1 = self._read_in_plist()

        self.set_specs(["rootpkg:run"])
        subset.compute_subset(self.cfg, self.sess)
        files2 = self._read_in_plist()

        assert files1 == files2


class Test_SkipMissingArchPkgs(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-missing_archpkg"),
                tlpdb=os.path.join(DIRPATH, "error_missing_archpkg.tlpdb"),
                arch="amd64-linux",
                dirs=False
                )

        super(Test_SkipMissingArchPkgs, self).setup_method(method)

    def test_missing_archpkg(self):
        self.cfg.inc_pkgspecs = ["rootpkg"]
        self.cfg.skip_missing_archpkgs = True

        # This should not raise
        subset.compute_subset(self.cfg, self.sess)

        # And we should have no files
        files = self._read_in_plist()
        assert len(files) == 0
