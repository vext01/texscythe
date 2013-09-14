import os.path, pytest, sys

MYPATH = os.path.abspath(__file__)
DIRPATH = os.path.dirname(MYPATH)
DBPATH = os.path.join(DIRPATH, "basic.db")
TLPDBPATH = os.path.join(DIRPATH, "basic.tlpdb")
PLISTPATH = os.path.join(DIRPATH, "PLIST-basic")

sys.path.append(os.path.join(DIRPATH, ".."))
from orm import File, Package
import tlpdbparser, subset

class Test_Basic(object):

    def setup_class(self):
        self.config = {
            "sqldb"             : DBPATH,
            "plist"             : PLISTPATH,
            "prefix_filenames"  : "",
            "tlpdb"             : TLPDBPATH,
            "arch"              : None,
        }

        self.sess = tlpdbparser.initdb(self.config, return_sess=True)

    def teardown_class(self):
        self.sess.close()
        os.unlink(self.config["sqldb"])
        os.unlink(self.config["plist"])

    def test_stats(self):
        assert self.sess.query(File).count() == 7
        assert self.sess.query(Package).count() == 3

    def test_plist(self):
        subset.compute_subset(self.config, ["rootpkg"], None, self.sess)

        with open(self.config["plist"], "r") as f:
            lines = f.read()

        files = sorted([ x for x in lines.split("\n") if x != "" ])

        expected = sorted([ "runfiles/runfile%d" % x for x in range(1, 4) ] + \
            [ "docfiles/docfile%d" % x for x in range(1, 3) ] + \
            [ "srcfiles/srcfile1" ])
