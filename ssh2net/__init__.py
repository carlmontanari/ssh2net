"""ssh2net network ssh client library"""
import logging
from logging import NullHandler

from ssh2net.base import SSH2Net
from ssh2net.channel import SSH2NetChannel
from ssh2net.session import SSH2NetSession
from ssh2net.netmiko_compatibility import connect_handler as ConnectHandler
from ssh2net.ssh_config import SSH2NetSSHConfig
from ssh2net.core.driver import BaseNetworkDriver
from ssh2net.core.cisco_iosxe.driver import IOSXEDriver
from ssh2net.core.cisco_nxos.driver import NXOSDriver
from ssh2net.core.cisco_iosxr.driver import IOSXRDriver
from ssh2net.core.arista_eos.driver import EOSDriver
from ssh2net.core.juniper_junos.driver import JunosDriver

__version__ = "2019.10.27"
__all__ = (
    "SSH2Net",
    "SSH2NetSession",
    "SSH2NetChannel",
    "SSH2NetSSHConfig",
    "ConnectHandler",
    "BaseNetworkDriver",
    "IOSXEDriver",
    "NXOSDriver",
    "IOSXRDriver",
    "EOSDriver",
    "JunosDriver",
)


# Class to filter duplicate log entries for the channel logger
# Stolen from: https://stackoverflow.com/questions/44691558/ \
# suppress-multiple-messages-with-same-content-in-python-logging-module-aka-log-co
class DuplicateFilter(logging.Filter):
    def filter(self, record):
        # Fields to compare to previous log entry if these fields match; skip log entry
        current_log = (record.module, record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            return True
        return False


# Setup session logger
session_log = logging.getLogger(f"{__name__}_session")
logging.getLogger(f"{__name__}_session").addHandler(NullHandler())

# Setup channel logger
channel_log = logging.getLogger(f"{__name__}_channel")
# Add duplicate filter to channel log
channel_log.addFilter(DuplicateFilter())
logging.getLogger(f"{__name__}_channel").addHandler(NullHandler())
