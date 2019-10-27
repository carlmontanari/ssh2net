"""ssh2net.core.arista_eos.driver"""
import re
from typing import Any, Dict

from ssh2net.core.driver import BaseNetworkDriver, PrivilegeLevel


EOS_ARG_MAPPER = {
    "comms_prompt_regex": r"^[a-z0-9.\-@()/:]{1,32}[#>$]$",
    "comms_return_char": "\n",
    "comms_pre_login_handler": "",
    "comms_disable_paging": "terminal length 0",
}

PRIVS = {
    "exec": (
        PrivilegeLevel(
            re.compile(r"^[a-z0-9.\-@()/:]{1,32}>$", flags=re.M | re.I),
            "exec",
            None,
            None,
            "privilege_exec",
            "enable",
            True,
            "Password:",
            True,
            0,
        )
    ),
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


class EOSDriver(BaseNetworkDriver):
    def __init__(self, **kwargs: Dict[str, Any]):
        """
        Initialize SSH2Net EOSDriver Object

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
        self.textfsm_platform = "arista_eos"
