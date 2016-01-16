import os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset, config


class Test_Basic(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-basic"),
                tlpdb=os.path.join(DIRPATH, "basic.tlpdb"),
                dirs=False
                )

        super(Test_Basic, self).setup_method(method)

    def test_stats(self):
        assert self.sess.query(File).count() == 13
        assert self.sess.query(Package).count() == 7

    def test_plist(self):
        self.set_specs(["rootpkg"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        expected = sorted(
            ["runfiles/runfile%d" % x for x in range(1, 4)] +
            ["docfiles/docfile%d" % x for x in range(1, 3)] +
            ["srcfiles/srcfile1"]
        )

        assert files == expected

    def test_plist_runfiles(self):
        self.set_specs(["rootpkg:run"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()
        expected = sorted(["runfiles/runfile%d" % x for x in range(1, 4)])

        assert files == expected

    def test_plist_docfiles(self):
        self.set_specs(["rootpkg:doc"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()
        expected = sorted(["docfiles/docfile%d" % x for x in range(1, 3)])

        assert files == expected

    def test_plist_srcfiles(self):
        self.set_specs(["rootpkg:src"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == ["srcfiles/srcfile1"]

    def test_plist_binfiles(self):
        self.set_specs(["rootpkg:bin"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        # Since we didn't supply an arch and the only binfile that appears is
        # in an arch specific package, we should not see it in the plist
        assert files == []

    def test_plist_runfiles_docfiles(self):
        self.set_specs(["rootpkg:run,doc"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()
        expected = sorted(
            ["runfiles/runfile%d" % x for x in range(1, 4)] +
            ["docfiles/docfile%d" % x for x in range(1, 3)]
        )

        assert files == expected

    def test_plist_no_docfiles(self):
        self.set_specs(["rootpkg"], ["rootpkg:doc"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        expected = sorted(
            ["runfiles/runfile%d" % x for x in range(1, 4)] +
            ["srcfiles/srcfile1"]
        )

        assert files == expected

    def test_plist_exlude_all(self):
        self.set_specs(["rootpkg"], ["rootpkg"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == []

    def test_filename_prefix(self):
        self.cfg.prefix_filenames = "share/"
        self.set_specs(["rootpkg:src"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == ["share/srcfiles/srcfile1"]

    def test_filename_prefix2(self):
        self.cfg.prefix_filenames = "share/"
        self.cfg.plist = None  # Return file list
        self.set_specs(["rootpkg:src"])
        files = subset.compute_subset(self.cfg, self.sess)

        assert files == ["share/srcfiles/srcfile1"]

    def test_nowrite_plist(self):
        self.set_specs(["rootpkg"])
        self.cfg.plist = None  # don't write plist, return set
        files = subset.compute_subset(self.cfg, self.sess)

        expected = sorted(
                ["runfiles/runfile%d" % x for x in range(1, 4)] +
                ["docfiles/docfile%d" % x for x in range(1, 3)] +
                ["srcfiles/srcfile1"]
        )

        assert files == expected

    def test_nodepend(self):
        self.set_specs(["!rootpkg"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == []

    def test_nodepend2(self):
        self.set_specs(["!test_nodepend_pkg:run"])
        subset.compute_subset(self.cfg, self.sess)
        files = self._read_in_plist()

        assert files == ["a_file_we_should_find"]

    def test_database_path0001(self):
        db = os.path.join(DIRPATH, "basic.tlpdb.db")
        assert self.cfg.sqldb == db
        assert os.path.exists(db)
