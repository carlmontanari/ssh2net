"""ssh2net.core.juniper_junos.helper"""
from ssh2net.core import JunosDriver


def disable_paging(cls: JunosDriver) -> None:
    """
    Disable paging and set screen width for Junos

    Args:
        cls: SSH2NetSocket connection object

    Returns:
        N/A  # noqa

    Raises:
        N/A  # noqa
    """
    cls.send_inputs("set cli screen-length 0")
    cls.send_inputs("set cli screen-width 511")
