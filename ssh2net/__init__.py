"""ssh2net network ssh client library"""
import logging
from logging import NullHandler

from ssh2net.base import SSH2Net, SSH2NetChannel, SSH2NetSession


logger = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(NullHandler())

__version__ = "2019.09.02"
__all__ = ("SSH2Net", "SSH2NetChannel", "SSH2NetSession")
