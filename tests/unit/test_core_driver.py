import sys

import pytest

from ssh2net.exceptions import UnknownPrivLevel
from ssh2net.core.driver import BaseNetworkDriver
from ssh2net.core.cisco_iosxe.driver import PRIVS


IOS_ARP = """Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  172.31.254.1            -   0000.0c07.acfe  ARPA   Vlan254
Internet  172.31.254.2            -   c800.84b2.e9c2  ARPA   Vlan254
"""


def test__determine_current_priv():
    base_driver = BaseNetworkDriver()
    base_driver.privs = PRIVS
    current_priv = base_driver._determine_current_priv("execprompt>")
    assert current_priv.name == "exec"


def test__determine_current_priv_unknown():
    base_driver = BaseNetworkDriver()
    base_driver.privs = PRIVS
    with pytest.raises(UnknownPrivLevel):
        base_driver._determine_current_priv("!!!!thisissoooowrongggg!!!!!!?!")


@pytest.mark.skipif(sys.platform.startswith("win"), reason="not supporting textfsm on windows")
def test_textfsm_parse_output():
    base_driver = BaseNetworkDriver()
    base_driver.textfsm_platform = "cisco_ios"
    result = base_driver.textfsm_parse_output("show ip arp", IOS_ARP)
    assert isinstance(result, list)
    assert result[0] == ["Internet", "172.31.254.1", "-", "0000.0c07.acfe", "ARPA", "Vlan254"]
