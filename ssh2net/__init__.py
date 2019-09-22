"""ssh2net network ssh client library"""
import logging
from logging import NullHandler

from ssh2net.base import SSH2Net, SSH2NetChannel, SSH2NetSession
from ssh2net.helper import ConnectHandler
from ssh2net.ssh_config import SSH2NetSSHConfig


__version__ = "2019.09.21"
__all__ = ("SSH2Net", "SSH2NetChannel", "SSH2NetSession", "SSH2NetSSHConfig", "ConnectHandler")


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
