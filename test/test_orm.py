import os
from helper import AbstractTest, DIRPATH

from texscythe.orm import check_sqldb
from texscythe import config


class Test_ORM(AbstractTest):
    def setup_method(self, method):
        self.cfg = config.Config(
                plist=os.path.join(DIRPATH, "PLIST-basic"),
                tlpdb=os.path.join(DIRPATH, "basic.tlpdb"),
                dirs=False
                )

        super(Test_ORM, self).setup_method(method)

    def test_up_to_date0001(self):
        """The database has been created by setup_method and is now up to date.
        re-initialising the db should not be necessary."""

        create, update = check_sqldb(self.cfg)
        assert not create
        assert not update

    def test_non_existent0001(self):
        """We remove the database. Creation should be necessary."""

        self.sess.close()
        os.unlink(self.cfg.sqldb)

        create, update = check_sqldb(self.cfg)
        assert create
        assert not update

    def test_ood0001(self):
        """Out of date. Update is necessary"""

        os.utime(self.cfg.tlpdb, None)   # aka. touch

        create, update = check_sqldb(self.cfg)
        assert not create
        assert update
