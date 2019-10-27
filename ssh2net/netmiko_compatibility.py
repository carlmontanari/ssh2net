"""ssh2net.netmiko_compatibility"""
from ssh2net.core.cisco_iosxe.driver import IOSXEDriver, IOSXE_ARG_MAPPER
from ssh2net.core.cisco_nxos.driver import NXOSDriver, NXOS_ARG_MAPPER
from ssh2net.core.cisco_iosxr.driver import IOSXRDriver, IOSXR_ARG_MAPPER
from ssh2net.core.arista_eos.driver import EOSDriver, EOS_ARG_MAPPER
from ssh2net.core.juniper_junos.driver import JunosDriver, JUNOS_ARG_MAPPER

NETMIKO_DEVICE_TYPE_MAPPER = {
    "cisco_ios": {"driver": IOSXEDriver, "arg_mapper": IOSXE_ARG_MAPPER},
    "cisco_xe": {"driver": IOSXEDriver, "arg_mapper": IOSXE_ARG_MAPPER},
    "cisco_nxos": {"driver": NXOSDriver, "arg_mapper": NXOS_ARG_MAPPER},
    "cisco_xr": {"driver": IOSXRDriver, "arg_mapper": IOSXR_ARG_MAPPER},
    "arista_eos": {"driver": EOSDriver, "arg_mapper": EOS_ARG_MAPPER},
    "juniper_junos": {"driver": JunosDriver, "arg_mapper": JUNOS_ARG_MAPPER},
}

VALID_SSH2NET_KWARGS = {
    "setup_host",
    "setup_validate_host",
    "setup_port",
    "setup_timeout",
    "setup_ssh_config_file",
    "session_keepalive",
    "session_keepalive_interval",
    "session_timeout",
    "auth_user",
    "auth_password",
    "auth_public_key",
    "comms_prompt_regex",
    "comms_operation_timeout",
    "comms_return_char",
    "comms_pre_login_handler",
    "comms_disable_paging",
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
