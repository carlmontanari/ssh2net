"""ssh2net.core.driver"""
import collections
import re
from typing import Any, Dict, Optional, Union

from ssh2net.base import SSH2Net
from ssh2net.exceptions import UnknownPrivLevel
from ssh2net.helper import _textfsm_get_template, textfsm_parse


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


class BaseNetworkDriver(SSH2Net):
    def __init__(self, auth_secondary: Optional[Union[str]] = None, **kwargs: Dict[str, Any]):
        """
        Initialize SSH2Net BaseNetworkDriver Object

        Args:
            auth_secondary: password to use for secondary authentication (enable)

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        self.auth_secondary = auth_secondary
        super().__init__(**kwargs)
        self.privs = PRIVS
        self.default_desired_priv = None
        self.textfsm_platform = None

    def _determine_current_priv(self, current_prompt: str):
        """
        Determine current privilege level from prompt string

        Args:
            current_prompt: string of current prompt

        Returns:
            priv_level: NamedTuple of current privilege level

        Raises:
            UnknownPrivLevel: if privilege level cannot be determined  # noqa
            # darglint raises DAR401 for some reason hence the noqa...

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
                        self.auth_enable,
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

    def send_command(self, commands):
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

    def send_config_set(self, configs):
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
        result = self.send_inputs(configs)
        self.attain_priv(self.default_desired_priv)
        return result

    def textfsm_parse_output(self, command: str, output: str) -> str:
        """
        Parse output with TextFSM and ntc-templates

        Args:
            command: command used to get output
            output: output from command

        Returns:
            output: parsed output

        Raises:
            N/A  # noqa
        """
        template = _textfsm_get_template(self.textfsm_platform, command)
        if template:
            output = textfsm_parse(template, output)
        return output
