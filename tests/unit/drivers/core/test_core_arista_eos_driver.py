from ssh2net.core.arista_eos.driver import EOSDriver, PRIVS
from tests.unit.drivers.base_driver_unit_tests import BaseDriverUnitTest


class TestEOS(BaseDriverUnitTest):
    def setup_method(self):
        self.privs = PRIVS
        self.driver = EOSDriver()
