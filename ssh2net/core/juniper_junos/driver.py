"""ssh2net.core.juniper_junos.driver"""
import re
from typing import Any, Dict

from ssh2net.core.driver import BaseNetworkDriver, PrivilegeLevel


JUNOS_ARG_MAPPER = {
    "comms_prompt_regex": r"^[a-z0-9.\-@()/:]{1,32}[#>$]$",
    "comms_return_char": "\n",
    "comms_pre_login_handler": "",
    "comms_disable_paging": "ssh2net.core.juniper_junos.helper.disable_paging",
}

PRIVS = {
    "exec": (
        PrivilegeLevel(
            re.compile(r"^[a-z0-9.\-@()/:]{1,32}>$", flags=re.M | re.I),
            "exec",
            None,
            None,
            "configuration",
            "configure",
            False,
            False,
            True,
            0,
        )
    ),
    "configuration": (
        PrivilegeLevel(
            re.compile(r"^[a-z0-9.\-@()/:]{1,32}#$", flags=re.M | re.I),
            "configuration",
            "exec",
            "exit configuration-mode",
            None,
            None,
            False,
            False,
            True,
            1,
        )
    ),
}


class JunosDriver(BaseNetworkDriver):
    def __init__(self, **kwargs: Dict[str, Any]):
        """
        Initialize SSH2Net IOSXEDriver Object

        Args:
            **kwargs: keyword args to pass to inherited class(es)

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        super().__init__(**kwargs)
        self.privs = PRIVS
        self.default_desired_priv = "exec"
