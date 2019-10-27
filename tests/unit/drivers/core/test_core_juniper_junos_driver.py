import pytest

from ssh2net.core.juniper_junos.driver import JunosDriver, PRIVS
from tests.unit.drivers.base_driver_unit_tests import BaseDriverUnitTest


class TestIOSXE(BaseDriverUnitTest):
    def setup_method(self):
        self.privs = PRIVS
        self.driver = JunosDriver()

    def test__determine_current_priv_privilege_exec(self):
        pytest.skip("no privilege exec on junos")

    def test__determine_current_priv_config(self):
        assert self.driver._determine_current_priv("myrouter#") == self.privs["configuration"]

    def test__determine_current_priv_special_config(self):
        pytest.skip("not testing for special config pattern on juniper")
