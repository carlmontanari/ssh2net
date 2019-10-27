import pytest

from ssh2net.core.cisco_iosxr.driver import IOSXRDriver, PRIVS
from tests.unit.drivers.base_driver_unit_tests import BaseDriverUnitTest


class TestIOSXR(BaseDriverUnitTest):
    def setup_method(self):
        self.privs = PRIVS
        self.driver = IOSXRDriver()

    def test__determine_current_priv_exec(self):
        pytest.skip("no privilege exec on iosxr")
