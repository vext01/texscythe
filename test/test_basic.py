import pytest, sys, os.path
from helper import AbstractTest, DIRPATH

from texscythe.orm import File, Package
from texscythe import subset

class Test_Basic(AbstractTest):

    def setup_method(self, method):
        self.config = {
            "sqldb"             : os.path.join(DIRPATH, "basic.db"),
            "plist"             : os.path.join(DIRPATH, "PLIST-basic"),
            "prefix_filenames"  : "",
            "tlpdb"             : os.path.join(DIRPATH, "basic.tlpdb"),
            "arch"              : None,
        }

        super(Test_Basic, self).setup_method(method)

    def test_stats(self):
        assert self.sess.query(File).count() == 7
        assert self.sess.query(Package).count() == 3

    def test_plist(self):
        subset.compute_subset(self.config, ["rootpkg"], None, self.sess)
        files = self._read_in_plist()

        expected = sorted([ "runfiles/runfile%d" % x for x in range(1, 4) ] + \
            [ "docfiles/docfile%d" % x for x in range(1, 3) ] + \
            [ "srcfiles/srcfile1" ])

        assert files == expected

    def test_plist_runfiles(self):
        subset.compute_subset(self.config, ["rootpkg:run"], None, self.sess)
        files = self._read_in_plist()
        expected = sorted([ "runfiles/runfile%d" % x for x in range(1, 4) ])

        assert files == expected

    def test_plist_docfiles(self):
        subset.compute_subset(self.config, ["rootpkg:doc"], None, self.sess)
        files = self._read_in_plist()
        expected = sorted([ "docfiles/docfile%d" % x for x in range(1, 3) ])

        assert files == expected

    def test_plist_srcfiles(self):
        subset.compute_subset(self.config, ["rootpkg:src"], None, self.sess)
        files = self._read_in_plist()

        assert files == ["srcfiles/srcfile1"]

    def test_plist_binfiles(self):
        subset.compute_subset(self.config, ["rootpkg:bin"], None, self.sess)
        files = self._read_in_plist()

        # Since we didn't supply an arch and the only binfile that appears is
        # in an arch specific package, we should not see it in the plist
        assert files == []

    def test_plist_runfiles_docfiles(self):
        subset.compute_subset(self.config, ["rootpkg:run,doc"], None, self.sess)
        files = self._read_in_plist()
        expected = sorted(
            [ "runfiles/runfile%d" % x for x in range(1, 4) ] +
            [ "docfiles/docfile%d" % x for x in range(1, 3) ]
        )

        assert files == expected

    def test_plist_no_docfiles(self):
        subset.compute_subset(self.config,
                ["rootpkg"], ["rootpkg:doc"], self.sess)
        files = self._read_in_plist()

        expected = sorted([ "runfiles/runfile%d" % x for x in range(1, 4) ] +
                [ "srcfiles/srcfile1" ])

        assert files == expected

    def test_plist_exlude_all(self):
        subset.compute_subset(self.config,
                ["rootpkg"], ["rootpkg"], self.sess)
        files = self._read_in_plist()

        assert files == []

class Test_BasicWithArch(AbstractTest):

    def setup_method(self, method):
        self.config = {
            "sqldb"             : os.path.join(DIRPATH, "basic_arch.db"),
            "plist"             : os.path.join(DIRPATH, "PLIST-basic_arch"),
            "prefix_filenames"  : "",
            "tlpdb"             : os.path.join(DIRPATH, "basic.tlpdb"),
            "arch"              : "amd64-linux",
        }

        super(Test_BasicWithArch, self).setup_method(method)

    def test_plist_binfiles(self):
        subset.compute_subset(self.config, ["rootpkg:bin"], None, self.sess)
        files = self._read_in_plist()

        # Since we *did* supply an arch we should see binfiles here
        assert files == ['binfiles/binfile1']

# XXX:
# test multiple include/exclude
# test explicit everything 'run,src,doc,bin'
# Test error cases
