"""ssh2net.core.juniper_junos.driver"""
import re

from ssh2net.core.driver import BaseDriver, PrivilegeLevel


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


class JunosDriver(BaseDriver):
    def __init__(self, conn):
        """
        Initialize SSH2Net IOSXEDriver Object

        Args:
            conn: ssh2net connection object

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        super().__init__(conn)
        self.base_conn = conn
        self.get_prompt = conn.get_prompt
        self.send_inputs = conn.send_inputs
        self.send_inputs_interact = conn.send_inputs_interact
        self.privs = PRIVS
        self.default_desired_priv = "exec"
