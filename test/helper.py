import os, os.path, sys

# adjust paths
MYPATH = os.path.abspath(__file__)
DIRPATH = os.path.dirname(MYPATH)
sys.path.append(os.path.join(DIRPATH, ".."))
from texscythe import tlpdbparser

class AbstractTest(object):
    """ Common functionality for tests """

    def setup_method(self, method):
        self.sess = tlpdbparser.initdb(self.cfg, return_sess=True)

    def teardown_method(self, method):
        self.sess.close()
        try:
            os.unlink(self.cfg.sqldb)
        except:
            pass

        try:
            os.unlink(self.cfg.plist)
        except:
            pass

    def _read_in_plist(self):
        """ returns a list of filenames (sorted) """
        with open(self.cfg.plist, "r") as f:
            lines = f.read()
        return sorted([ x for x in lines.split("\n") if x != "" ])

    def set_specs(self, inc=[], exc=[]):
        self.cfg.inc_pkgspecs = inc
        self.cfg.exc_pkgspecs = exc
