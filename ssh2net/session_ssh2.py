"""ssh2net.session_ssh2"""
import logging

from ssh2.session import Session
from ssh2.exceptions import AuthenticationError

from ssh2net.exceptions import AuthenticationFailed


class SSH2NetSessionSSH2:
    def __init__(self, p_self):
        """
        Initialize SSH2NetSessionSSH2 Object

        This is the default underlying "driver" for ssh2net. This has been pulled out of the
        "base" SSH2NetSession class to provide a mechanism for supporting both "ssh2-python" and
        "paramiko".

        Args:
            p_self: SSH2Net object

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.__dict__ = p_self.__dict__
        self._session_alive = p_self._session_alive
        self._session_open = p_self._session_open
        self._channel_alive = p_self._channel_alive

    def _session_open_connect(self) -> None:
        """
        Perform session handshake

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            Exception: catch all for unknown exceptions during session handshake

        """
        self.session = Session()
        if self.session_timeout:
            self.session.set_timeout(self.session_timeout)
        try:
            self.session.handshake(self.sock)
        except Exception as exc:
            logging.critical(
                f"Failed to complete handshake with host {self.host}; " f"Exception: {exc}"
            )
            raise exc

    def _session_public_key_auth(self) -> None:
        """
        Perform public key based auth on SSH2NetSession

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            Exception: catch all for unhandled exceptions

        """
        try:
            self.session.userauth_publickey_fromfile(self.auth_user, self.auth_public_key)
        except AuthenticationError:
            logging.critical(f"Public key authentication with host {self.host} failed. ")
        except Exception as exc:
            logging.critical(
                "Unknown error occurred during public key authentication with host "
                f"{self.host}; Exception: {exc}"
            )
            raise exc

    def _session_password_auth(self) -> None:
        """
        Perform password based auth on SSH2NetSession

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            AuthenticationFailed: if authentication fails
            Exception: catch all for unknown other exceptions

        """
        try:
            self.session.userauth_password(self.auth_user, self.auth_password)
        except AuthenticationError as exc:
            logging.critical(
                f"Password authentication with host {self.host} failed. Exception: {exc}."
                f"\n\tTrying keyboard interactive auth..."
            )
            try:
                self.session.userauth_keyboardinteractive(self.auth_user, self.auth_password)
            except AuthenticationError as exc:
                logging.critical(
                    f"Keyboard interactive authentication with host {self.host} failed. "
                    f"Exception: {exc}."
                )
                raise AuthenticationFailed
            except Exception as exc:
                logging.critical(
                    "Unknown error occurred during keyboard interactive authentication with host "
                    f"{self.host}; Exception: {exc}"
                )
                raise exc
        except Exception as exc:
            logging.critical(
                "Unknown error occurred during password authentication with host "
                f"{self.host}; Exception: {exc}"
            )
            raise exc

    def _channel_open_driver(self) -> None:
        """
        Open channel

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.channel = self.session.open_session()
        self.channel.pty()
        logging.debug(f"Channel to host {self.host} opened")

    def _channel_invoke_shell(self) -> None:
        """
        Invoke shell on channel

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self._shell = True
        self.channel.shell()
