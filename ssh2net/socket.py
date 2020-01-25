"""ssh2net.base"""
import logging
import socket

from ssh2net.exceptions import SetupTimeout

SOCKET_LOG = logging.getLogger("ssh2net_socket")


class SSH2NetSocket:
    """
    SSH2NetSocket

    SSH2Net <- SSH2NetChannel <- SSH2NetSession <- SSH2NetSocket

    SSH2NetSession is responsible for handling the actual socket that the SSH session uses.

    The following arguments are type hinted here at the base class. ssh2net uses a mixin type
    structure to divide each logical component of the overall ssh2net object into its own class.
    Because of the mixin structure there are no init methods in the Channel, Session, or Socket
    classes. In order to appease mypy and ensure that ssh2net is typed reasonably well the typing
    information for these classes are done at the class level as found here.

    """

    host: str
    port: int
    setup_timeout: int

    def _socket_alive(self) -> bool:
        """
        Check if underlying socket is alive

        Args:
            N/A  # noqa

        Returns:
            bool True/False if socket is alive

        Raises:
            N/A  # noqa

        """
        try:
            self.sock.send(b"")
            return True
        except OSError:
            # socket is not alive
            SOCKET_LOG.debug(f"Socket to host {self.host} is not alive")
            return False
        except AttributeError:
            # socket never created yet
            SOCKET_LOG.debug(f"Socket to host {self.host} has never been created")
            return False

    def _socket_open(self) -> None:
        """
        Open underlying socket

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            SetupTimeout: if socket connection times out

        """
        if not self._socket_alive():
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.setup_timeout)
            try:
                self.sock.connect((self.host, self.port))
            except socket.timeout:
                SOCKET_LOG.critical(
                    f"Timed out trying to open socket to {self.host} on port {self.port}"
                )
                raise SetupTimeout(
                    f"Timed out trying to open socket to {self.host} on port {self.port}"
                )
            SOCKET_LOG.debug(f"Socket to host {self.host} opened")

    def _socket_close(self) -> None:
        """
        Close underlying socket

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if self._socket_alive():
            self.sock.close()
            SOCKET_LOG.debug(f"Socket to host {self.host} closed")
