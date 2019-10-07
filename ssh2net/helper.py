"""ssh2net.helper"""
import importlib
from io import TextIOWrapper
import pkg_resources  # pylint: disable=C0411
import warnings

from ssh2net.core.cisco_iosxe.driver import IOSXEDriver, IOSXE_ARG_MAPPER
from ssh2net.core.cisco_nxos.driver import NXOSDriver, NXOS_ARG_MAPPER
from ssh2net.core.juniper_junos.driver import JunosDriver, JUNOS_ARG_MAPPER

NETMIKO_DEVICE_TYPE_MAPPER = {
    "cisco_ios": {"driver": IOSXEDriver, "arg_mapper": IOSXE_ARG_MAPPER},
    "cisco_xe": {"driver": IOSXEDriver, "arg_mapper": IOSXE_ARG_MAPPER},
    "cisco_nxos": {"driver": NXOSDriver, "arg_mapper": NXOS_ARG_MAPPER},
    "juniper_junos": {"driver": JunosDriver, "arg_mapper": JUNOS_ARG_MAPPER},
}

VALID_SSH2NET_KWARGS = [
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
    "comms_prompt_timeout",
    "comms_return_char",
    "comms_pre_login_handler",
    "comms_disable_paging",
]


def validate_external_function(possible_function):
    """
    Validate string representing external function is a callable

    Args:
        possible_function: string "pointing" to external function

    Returns:
        None/Callable: None or callable function

    Raises:
        N/A  # noqa

    """
    try:
        if not isinstance(possible_function, str):
            return None
        if "." not in possible_function:
            return None
        ext_func_path = possible_function.split(".")
        ext_module = ".".join(ext_func_path[:-1])
        ext_function = ext_func_path[-1]
        ext_module = importlib.import_module(ext_module)
        return getattr(ext_module, ext_function)
    except ModuleNotFoundError:
        return None


def ConnectHandler(**kwargs):
    """
    Convert netmiko style ConnectHandler device creation to SSH2Net style

    Args:
        **kwargs: keyword arguments

    Returns:
        driver: SSH2Net connection object for specified device-type

    Raises:
        TypeError: if unsupported netmiko device type is provided

    """
    from ssh2net.base import SSH2Net

    if kwargs["device_type"] not in NETMIKO_DEVICE_TYPE_MAPPER.keys():
        raise TypeError(f"Unsupported netmiko device type for ssh2net: {kwargs['device_type']}")

    driver_info = NETMIKO_DEVICE_TYPE_MAPPER.get(kwargs["device_type"])
    driver = driver_info["driver"]
    driver_args = driver_info["arg_mapper"]
    kwargs.pop("device_type")

    transformed_kwargs = transform_netmiko_kwargs(kwargs)
    final_kwargs = {**transformed_kwargs, **driver_args}

    conn = SSH2Net(**final_kwargs)
    conn.open_shell()
    driver = driver(conn)

    return driver


def transform_netmiko_kwargs(kwargs):
    """
    Transform netmiko style ConnectHandler arguments to ssh2net style

    Args:
        kwargs: netmiko-style ConnectHandler kwargs to transform to ssh2net style

    Returns:
        transformed_kwargs: converted keyword arguments

    """
    kwargs["setup_host"] = kwargs.pop("host")
    kwargs["setup_validate_host"] = False
    kwargs["setup_port"] = kwargs.pop("port", 22)
    kwargs["setup_timeout"] = 5
    kwargs["setup_ssh_config_file"] = kwargs.pop("ssh_config_file", False)
    kwargs["session_keepalive"] = False
    kwargs["session_keepalive_interval"] = 10
    kwargs["auth_user"] = kwargs.pop("username")
    kwargs["auth_password"] = kwargs.pop("password", None)
    kwargs["auth_public_key"] = kwargs.pop("key_file", None)
    kwargs["comms_prompt_regex"] = ""
    kwargs["comms_prompt_timeout"] = 10
    if "global_delay_factor" in kwargs.keys():
        kwargs["comms_prompt_timeout"] = kwargs["global_delay_factor"] * 10
        kwargs.pop("global_delay_factor")
    else:
        kwargs["comms_prompt_timeout"] = 5
    kwargs["comms_return_char"] = ""
    kwargs["comms_pre_login_handler"] = ""
    kwargs["comms_disable_paging"] = ""

    transformed_kwargs = {k: v for (k, v) in kwargs.items() if k in VALID_SSH2NET_KWARGS}

    return transformed_kwargs


def _textfsm_get_template(platform: str, command: str):
    """
    Find correct TextFSM template based on platform and command executed

    Args:
        platform: ntc-templates device type; i.e. cisco_ios, arista_eos, etc.
        command: string of command that was executed (to find appropriate template)

    Returns:
        None or TextIOWrapper of opened template

    """
    try:
        from textfsm.clitable import CliTable
        import ntc_templates  # noqa
    except ModuleNotFoundError as e:
        err = f"Module '{e.name}' not installed!"
        msg = f"***** {err} {'*' * (80 - len(err))}"
        fix = (
            f"To resolve this issue, install '{e.name}'. You can do this in one of the following"
            " ways:\n"
            "1: 'pip install -r requirements-textfsm.txt'\n"
            "2: 'pip install ssh2net[textfsm]'"
        )
        warning = "\n" + msg + "\n" + fix + "\n" + msg
        warnings.warn(warning)
        return None
    template_dir = pkg_resources.resource_filename("ntc_templates", "templates")
    cli_table = CliTable("index", template_dir)
    template_index = cli_table.index.GetRowMatch({"Platform": platform, "Command": command})
    if not template_index:
        return None
    template_name = cli_table.index.index[template_index]["Template"]
    template = open(f"{template_dir}/{template_name}")
    return template


def textfsm_parse(template, output):
    """
    Parse output with TextFSM and ntc-templates, try to return structured output

    Args:
        template: TextIOWrapper or string path to template to use to parse data
        output: unstructured output from device to parse

    Returns:
        output: structured data

    """
    import textfsm  # noqa

    if not isinstance(template, TextIOWrapper):
        template = open(template)
    re_table = textfsm.TextFSM(template)
    try:
        output = re_table.ParseText(output)
        return output
    except textfsm.parser.TextFSMError:
        pass
    return output
