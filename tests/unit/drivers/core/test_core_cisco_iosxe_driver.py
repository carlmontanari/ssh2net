from ssh2net.core.cisco_iosxe.driver import IOSXEDriver, PRIVS
from tests.unit.drivers.base_driver_unit_tests import BaseDriverUnitTest


class TestIOSXE(BaseDriverUnitTest):
    def setup_method(self):
        self.privs = PRIVS
        self.driver = IOSXEDriver()
