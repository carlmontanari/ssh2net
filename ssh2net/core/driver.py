"""ssh2net.core.base"""
import collections
import re

from ssh2net.exceptions import UnknownPrivLevel

PrivilegeLevel = collections.namedtuple(
    "PrivLevel",
    "pattern "
    "name "
    "deescalate_priv "
    "deescalate "
    "escalate_priv "
    "escalate "
    "escalate_auth "
    "escalate_prompt "
    "requestable "
    "level",
)

PRIVS = {}


class BaseDriver:
    def __init__(self, conn):
        """
        Initialize SSH2Net BaseDriver Object

        Args:
            conn: ssh2net connection object

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        self.base_conn = conn
        self.get_prompt = conn.get_prompt
        self.send_inputs = conn.send_inputs
        self.send_inputs_interact = conn.send_inputs_interact
        self.privs = PRIVS
        self.default_desired_priv = None

    def _determine_current_priv(self, current_prompt):
        """
        Determine current privilege level from prompt string

        Args:
            current_prompt: string of current prompt

        Returns:
            priv_level: NamedTuple of current privilege level

        Raises:
            UnknownPrivLevel: if privilege level cannot be determined

        """
        for priv_level in self.privs.values():
            if re.search(priv_level.pattern, current_prompt):
                return priv_level
        raise UnknownPrivLevel

    def _escalate(self) -> None:
        """
        Escalate to the next privilege level up

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        current_priv = self._determine_current_priv(self.get_prompt())
        if current_priv.escalate:
            if current_priv.escalate_auth:
                self.send_inputs_interact(
                    (
                        current_priv.escalate,
                        current_priv.escalate_prompt,
                        self.base_conn.auth_enable,
                        self.privs.get("escalate_priv"),
                    ),
                    hidden_response=True,
                )
            else:
                self.send_inputs(current_priv.escalate)

    def _deescalate(self) -> None:
        """
        Deescalate to the next privilege level down

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        current_priv = self._determine_current_priv(self.get_prompt())
        if current_priv.deescalate:
            self.send_inputs(current_priv.deescalate)

    def attain_priv(self, desired_priv) -> None:
        """
        Attain desired priv level

        Args:
            desired_priv: string name of desired privilege level
                (see ssh2net.core.<device_type>.driver for levels)

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        while True:
            current_priv = self._determine_current_priv(self.get_prompt())
            if current_priv == self.privs[desired_priv]:
                return
            if current_priv.level > self.privs[desired_priv].level:
                self._deescalate()
            else:
                self._escalate()

    def send_command(self, commands) -> None:
        """
        Send command(s)

        Args:
            commands: string or list of strings to send to device in privilege exec mode

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        self.attain_priv(self.default_desired_priv)
        result = self.send_inputs(commands)
        return result

    def send_config_set(self, configs) -> None:
        """
        Send configuration(s)

        Args:
            configs: string or list of strings to send to device in config mode

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        self.attain_priv("configuration")
        self.send_inputs(configs)
        self.attain_priv(self.default_desired_priv)
