"""ssh2net.core.driver"""
import collections
import re
from typing import Any, Dict, List, Optional, Union

from ssh2net.base import SSH2NetBase
from ssh2net.exceptions import CouldNotAcquirePrivLevel, UnknownPrivLevel
from ssh2net.helper import _textfsm_get_template, textfsm_parse
from ssh2net.result import SSH2NetResult

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

PRIVS: Dict[str, PrivilegeLevel] = {}


class BaseNetworkDriver(SSH2NetBase):
    """BaseNetworkDriver"""

    def __init__(self, auth_secondary: Optional[Union[str]] = None, **kwargs: Any):
        """
        BaseNetworkDriver Object

        Args:
            auth_secondary: password to use for secondary authentication (enable)
            **kwargs: keyword args to pass to inherited class(es)

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        self.auth_secondary = auth_secondary
        super().__init__(**kwargs)
        self.privs = PRIVS
        self.default_desired_priv: Optional[str] = None
        self.textfsm_platform: str = ""

    def _determine_current_priv(self, current_prompt: str):
        """
        Determine current privilege level from prompt string

        Args:
            current_prompt: string of current prompt

        Returns:
            priv_level: NamedTuple of current privilege level

        Raises:
            UnknownPrivLevel: if privilege level cannot be determined  # noqa
            # NOTE: darglint raises DAR401 for some reason hence the noqa...

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
                        self.auth_secondary,
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

    def acquire_priv(self, desired_priv) -> None:
        """
        Acquire desired priv level

        Args:
            desired_priv: string name of desired privilege level
                (see ssh2net.core.<device_type>.driver for levels)

        Returns:
            N/A  # noqa

        Raises:
            CouldNotAcquirePrivLevel: if requested priv level not attained

        """
        priv_attempt_counter = 0
        while True:
            current_priv = self._determine_current_priv(self.get_prompt())
            if current_priv == self.privs[desired_priv]:
                return
            if priv_attempt_counter > len(self.privs):
                raise CouldNotAcquirePrivLevel(
                    f"Could not get to '{desired_priv}' privilege level."
                )

            if current_priv.level > self.privs[desired_priv].level:
                self._deescalate()
            else:
                self._escalate()
            priv_attempt_counter += 1

    def send_commands(
        self,
        commands: Union[str, List],
        strip_prompt: Optional[bool] = True,
        textfsm: Optional[bool] = False,
    ) -> List[SSH2NetResult]:
        """
        Send command(s)

        Args:
            commands: string or list of strings to send to device in privilege exec mode
            strip_prompt: True/False strip prompt from returned output
            textfsm: True/False try to parse each command with textfsm

        Returns:
            results: list of SSH2NetResult objects

        Raises:
            N/A  # noqa
        """
        self.acquire_priv(self.default_desired_priv)
        results = self.send_inputs(commands, strip_prompt)
        if not textfsm:
            return results
        for result in results:
            result.structured_result = self.textfsm_parse_output(
                result.channel_input, result.result
            )
        return results

    def send_configs(
        self, configs: Union[str, List], strip_prompt: Optional[bool] = True
    ) -> List[SSH2NetResult]:
        """
        Send configuration(s)

        Args:
            configs: string or list of strings to send to device in config mode
            strip_prompt: True/False strip prompt from returned output

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa
        """
        self.acquire_priv("configuration")
        result = self.send_inputs(configs, strip_prompt)
        self.acquire_priv(self.default_desired_priv)
        return result

    def textfsm_parse_output(self, command: str, output: str) -> Union[List, Dict[str, Any]]:
        """
        Parse output with TextFSM and ntc-templates

        Always return a non-string value -- if parsing fails to produce list/dict, return empty dict

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
        if isinstance(output, (dict, list)):
            return output
        return {}
