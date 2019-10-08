"""ssh2net.core.juniper_junos.helper"""


def disable_paging(cls):
    """
    Disable paging and set screen width for Junos

    Args:
        cls: SSH2Net connection object

    Returns:
        N/A  # noqa

    Raises:
        N/A  # noqa
    """
    cls.send_inputs("set cli screen-length 0")
    cls.send_inputs("set cli screen-width 511")
