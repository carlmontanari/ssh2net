from ssh2net.core.cisco_nxos.driver import NXOSDriver, PRIVS
from tests.unit.drivers.base_driver_unit_tests import BaseDriverUnitTest


class TestNXOS(BaseDriverUnitTest):
    def setup_method(self):
        self.privs = PRIVS
        self.driver = NXOSDriver()
