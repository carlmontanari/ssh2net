"""ssh2net.core.cisco_iosxr.driver"""
import re
import time
from typing import Any, Dict

from ssh2net.core.driver import BaseNetworkDriver, PrivilegeLevel


IOSXR_ARG_MAPPER = {
    "comms_prompt_regex": r"^[a-z0-9.\-@()/:]{1,32}[#>$]$",
    "comms_return_char": "\n",
    "comms_pre_login_handler": "",
    "comms_disable_paging": "terminal length 0",
}

PRIVS = {
    "privilege_exec": (
        PrivilegeLevel(
            re.compile(r"^[a-z0-9.\-@/:]{1,32}#$", flags=re.M | re.I),
            "privilege_exec",
            "exec",
            "disable",
            "configuration",
            "configure terminal",
            False,
            False,
            True,
            1,
        )
    ),
    "configuration": (
        PrivilegeLevel(
            re.compile(r"^[a-z0-9.\-@/:]{1,32}\(config\)#$", flags=re.M | re.I),
            "configuration",
            "priv",
            "end",
            None,
            None,
            False,
            False,
            True,
            2,
        )
    ),
    "special_configuration": (
        PrivilegeLevel(
            re.compile(r"^[a-z0-9.\-@/:]{1,32}\(config[a-z0-9.\-@/:]{1,16}\)#$", flags=re.M | re.I),
            "special_configuration",
            "priv",
            "end",
            None,
            None,
            False,
            False,
            False,
            3,
        )
    ),
}


def comms_pre_login_handler(cls):  # pylint: disable=W0613
    # sleep for session to establish; without this we never find base prompt
    time.sleep(1)


class IOSXRDriver(BaseNetworkDriver):
    def __init__(self, **kwargs: Dict[str, Any]):
        """
        Initialize SSH2Net IOSXRDriver Object

        Args:
            **kwargs: keyword args to pass to inherited class(es)

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        super().__init__(**kwargs)
        self.privs = PRIVS
        self.default_desired_priv = "privilege_exec"
        self.textfsm_platform = "cisco_xr"
