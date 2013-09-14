import os.path, pytest, sys

MYPATH = os.path.abspath(__file__)
DIRPATH = os.path.dirname(MYPATH)
DBPATH = os.path.join(DIRPATH, "basic.db")
TLPDBPATH = os.path.join(DIRPATH, "basic.tlpdb")
PLISTPATH = os.path.join(DIRPATH, "PLIST")

sys.path.append(os.path.join(DIRPATH, ".."))
from orm import File, Package

config = {
    "sqldb"             : DBPATH,
    "plist"             : PLISTPATH,
    "prefix_filenames"  : "",
    "tlpdb"             : TLPDBPATH,
    "arch"              : None,
}

class Test_Baisc(object):

    def setup_class(self):
        import tlpdbparser
        self.sess = tlpdbparser.initdb(config, return_sess=True)

    def test_stats(self):
        assert self.sess.query(File).count() == 7
        assert self.sess.query(Package).count() == 3
