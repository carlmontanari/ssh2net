"""ssh2net.netmiko_compatibility"""
import types
from typing import List, Union
import warnings

from ssh2net.core import IOSXEDriver
from ssh2net.core import NXOSDriver
from ssh2net.core import IOSXRDriver
from ssh2net.core import EOSDriver
from ssh2net.core import JunosDriver
from ssh2net.core.cisco_iosxe.driver import IOSXE_ARG_MAPPER
from ssh2net.core.cisco_nxos.driver import NXOS_ARG_MAPPER
from ssh2net.core.cisco_iosxr.driver import IOSXR_ARG_MAPPER
from ssh2net.core.arista_eos.driver import EOS_ARG_MAPPER
from ssh2net.core.juniper_junos.driver import JUNOS_ARG_MAPPER
from ssh2net.helper import _textfsm_get_template, textfsm_parse


VALID_SSH2NET_KWARGS = {
    "setup_host",
    "setup_validate_host",
    "setup_port",
    "setup_timeout",
    "setup_ssh_config_file",
    "setup_use_paramiko",
    "session_timeout",
    "session_keepalive",
    "session_keepalive_interval",
    "session_keepalive_type",
    "session_keepalive_pattern",
    "auth_user",
    "auth_password",
    "auth_public_key",
    "comms_strip_ansi",
    "comms_prompt_regex",
    "comms_operation_timeout",
    "comms_return_char",
    "comms_pre_login_handler",
    "comms_disable_paging",
}

NETMIKO_DEVICE_TYPE_MAPPER = {
    "cisco_ios": {"driver": IOSXEDriver, "arg_mapper": IOSXE_ARG_MAPPER},
    "cisco_xe": {"driver": IOSXEDriver, "arg_mapper": IOSXE_ARG_MAPPER},
    "cisco_nxos": {"driver": NXOSDriver, "arg_mapper": NXOS_ARG_MAPPER},
    "cisco_xr": {"driver": IOSXRDriver, "arg_mapper": IOSXR_ARG_MAPPER},
    "arista_eos": {"driver": EOSDriver, "arg_mapper": EOS_ARG_MAPPER},
    "juniper_junos": {"driver": JunosDriver, "arg_mapper": JUNOS_ARG_MAPPER},
}


def connect_handler(auto_open=True, **kwargs):
    """
    Convert netmiko style "ConnectHandler" device creation to SSH2Net style

    Args:
        auto_open: auto open connection or not (primarily for testing purposes)
        **kwargs: keyword arguments

    Returns:
        driver: SSH2Net connection object for specified device-type

    Raises:
        TypeError: if unsupported netmiko device type is provided

    """
    if kwargs["device_type"] not in NETMIKO_DEVICE_TYPE_MAPPER.keys():
        raise TypeError(f"Unsupported netmiko device type for ssh2net: {kwargs['device_type']}")

    driver_info = NETMIKO_DEVICE_TYPE_MAPPER.get(kwargs["device_type"])
    driver_class = driver_info["driver"]
    driver_args = driver_info["arg_mapper"]
    kwargs.pop("device_type")

    transformed_kwargs = transform_netmiko_kwargs(kwargs)
    final_kwargs = {**transformed_kwargs, **driver_args}

    driver = driver_class(**final_kwargs)

    # Below is a dirty way to patch netmiko methods into ssh2net without having a factory function
    # and a million classes... as this is just for testing interoperability we'll let this slide...
    driver.find_prompt = types.MethodType(netmiko_find_prompt, driver)
    driver.send_command = types.MethodType(netmiko_send_command, driver)
    driver.send_command_timing = types.MethodType(netmiko_send_command_timing, driver)
    driver.send_config_set = types.MethodType(netmiko_send_config_set, driver)

    if auto_open:
        driver.open_shell()

    return driver


def transform_netmiko_kwargs(kwargs):
    """
    Transform netmiko style ConnectHandler arguments to ssh2net style

    Args:
        kwargs: netmiko-style ConnectHandler kwargs to transform to ssh2net style

    Returns:
        transformed_kwargs: converted keyword arguments

    Raises:
        N/A  # noqa

    """
    host = kwargs.pop("host", None)
    ip = kwargs.pop("ip", None)
    kwargs["setup_host"] = host if host is not None else ip
    kwargs["setup_validate_host"] = False
    kwargs["setup_port"] = kwargs.pop("port", 22)
    kwargs["setup_timeout"] = 5
    kwargs["setup_ssh_config_file"] = kwargs.pop("ssh_config_file", False)
    kwargs["session_keepalive"] = False
    kwargs["session_keepalive_interval"] = 10
    if "global_delay_factor" in kwargs.keys():
        kwargs["session_timeout"] = kwargs["global_delay_factor"] * 5000
        kwargs.pop("global_delay_factor")
    else:
        kwargs["session_timeout"] = 5000
    kwargs["auth_user"] = kwargs.pop("username")
    kwargs["auth_password"] = kwargs.pop("password", None)
    kwargs["auth_public_key"] = kwargs.pop("key_file", None)
    kwargs["comms_prompt_regex"] = ""
    kwargs["comms_operation_timeout"] = 10
    kwargs["comms_return_char"] = ""
    kwargs["comms_pre_login_handler"] = ""
    kwargs["comms_disable_paging"] = ""

    transformed_kwargs = {k: v for (k, v) in kwargs.items() if k in VALID_SSH2NET_KWARGS}

    return transformed_kwargs


def netmiko_find_prompt(self) -> str:
    """
    Patch `find_prompt` in netmiko connect handler to `get_prompt` in ssh2net

    Args:
        N/A  # noqa

    Returns:
        N/A  # noqa

    Raises:
        N/A  # noqa

    """
    return self.get_prompt()


def netmiko_send_command(self, command_string: Union[str, List[str]], **kwargs) -> str:
    """
    Patch `send_command` in netmiko connect handler

    Patch and support strip_prompt, use_textfsm, and textfsm_template args. Return a single string
    to match netmiko functionality (instead of ssh2net result object)

    Args:
        self: do not use! this function gets patched in as a method and therefore needs a reference
            to the class instance.
        command_string: string or list of strings to send as commands
        **kwargs: keyword arguments to support other netmiko args without blowing up

    Returns:
        N/A  # noqa

    Raises:
        N/A  # noqa

    """
    strip_prompt = kwargs.pop("strip_prompt", True)
    expect_string = kwargs.pop("expect_string", None)
    use_textfsm = kwargs.pop("use_textfsm", False)
    textfsm_template = kwargs.pop("textfsm_template", None)

    if expect_string:
        err = "ssh2net netmiko interoperability does not support expect_string!"
        msg = f"***** {err} {'*' * (80 - len(err))}"
        fix = (
            f"To resolve this issue, use native or driver mode with `send_inputs_interact` method."
        )
        warning = "\n" + msg + "\n" + fix + "\n" + msg
        warnings.warn(warning)

    if isinstance(command_string, list):
        err = "netmiko does not support sending list of commands, using only the first command!"
        msg = f"***** {err} {'*' * (80 - len(err))}"
        fix = f"To resolve this issue, use native or driver mode with `send_inputs` method."
        warning = "\n" + msg + "\n" + fix + "\n" + msg
        warnings.warn(warning)
        command = command_string[0]
    else:
        command = command_string

    results = self.send_commands(command, strip_prompt)
    # netmiko supports sending single commands only and has no "result" object, peel out just result
    result = results[0].result

    if use_textfsm:
        if textfsm_template:
            structured_result = textfsm_parse(textfsm_template, result)
        else:
            textfsm_template = _textfsm_get_template(self.textfsm_platform, command)
            structured_result = textfsm_parse(textfsm_template, result)
        # netmiko returns unstructured data if no structured data was generated
        if structured_result:
            result = structured_result
    return result


def netmiko_send_command_timing(self, *args, **kwargs):
    """
    Patch `send_command_timing` in netmiko connect handler

    Really just a shim to send_command, ssh2net doesnt support/need timing mechanics -- adjust the
    timers on the connection object if needed, or adjust them on the fly in your code.

    Args:
        self: do not use! this function gets patched in as a method and therefore needs a reference
            to the class instance.
        *args: positional arguments to support other netmiko args without blowing up
        **kwargs: keyword arguments to support other netmiko args without blowing up

    Returns:
        N/A  # noqa

    Raises:
        N/A  # noqa

    """
    return self.send_command(*args, **kwargs)


def netmiko_send_config_set(self, config_commands: Union[str, List[str]], **kwargs) -> str:
    """
    Patch `send_config_set` in netmiko connect handler

    Note: ssh2net strips commands always (as it retains them in the result object anyway), so there
    is no interesting output from this as there would be in netmiko.

    Args:
        self: do not use! this function gets patched in as a method and therefore needs a reference
            to the class instance.
        config_commands: configuration command(s) to send to device
        **kwargs: keyword arguments to support other netmiko args without blowing up

    Returns:
        N/A  # noqa

    Raises:
        N/A  # noqa

    """
    strip_prompt = kwargs.pop("strip_prompt", True)
    enter_config_mode = kwargs.pop("enter_config_mode", True)
    exit_config_mode = kwargs.pop("exit_config_mode", True)

    if not enter_config_mode:
        results = self.send_commands(config_commands, strip_prompt)
    elif not exit_config_mode:
        self.acquire_priv("configuration")
        results = self.send_inputs(config_commands, strip_prompt)
    else:
        results = self.send_configs(config_commands, strip_prompt)
    # ssh2net always strips command, so there isn't typically anything useful coming back from this
    result = "\n".join([r.result for r in results])
    return result


def netmiko_send_config_from_file(self, config_file: str, **kwargs) -> str:
    """
    Patch `send_config_from_file` in netmiko connect handler

    Note: ssh2net strips commands always (as it retains them in the result object anyway), so there
    is no interesting output from this as there would be in netmiko.

    Args:
        self: do not use! this function gets patched in as a method and therefore needs a reference
            to the class instance.
        config_file: path to text file; will send each line as a config
        **kwargs: keyword arguments to support other netmiko args without blowing up

    Returns:
        N/A  # noqa

    Raises:
        N/A  # noqa

    """
    with open(config_file, "r") as f:
        config_commands = list(f)
    return self.send_config_set(config_commands, **kwargs)
