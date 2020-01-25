"""ssh2net.session_ssh2"""
import logging
import warnings

from ssh2net.exceptions import AuthenticationFailed, RequirementsNotSatisfied


class SSH2NetSessionSSH2:
    """SSH2NetSessionSSH2"""

    def __init__(self, p_self):
        """
        SSH2NetSessionSSH2 Object

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
        # due to somewhat shitty composition and problematic  multiple inheritance (how do i know to
        # inherit session_miko vs session_ssh2) we copy the base session object dict to the driver
        # session object dict. this angers mypy as it doesn't understand/like this darkness, so we
        # also explicitly map all of the vars that are created at time of instantiating this class
        # into this class so we have appropriate typing/hinting data... sorry...
        self.__dict__ = p_self.__dict__

        # mypy did not like these being set w/ setattr, so we'll do it manually
        self.sock = p_self.sock
        self.host = p_self.host
        self.auth_user = p_self.auth_user
        self.auth_password = p_self.auth_password
        self.auth_public_key = p_self.auth_public_key
        self.session_timeout = p_self.session_timeout

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
        try:
            from ssh2.session import Session  # pylint: disable=C0415
            from ssh2.exceptions import AuthenticationError, Timeout  # pylint: disable=C0415

            self.SSH2AuthenticationException = AuthenticationError
            self.session_driver_timeout_exception = Timeout
        except ModuleNotFoundError as exc:
            err = f"Module '{exc.name}' not installed!"
            msg = f"***** {err} {'*' * (80 - len(err))}"
            fix = (
                f"To resolve this issue, install '{exc.name}'. You can do this in one of the "
                "following ways:\n"
                "1: 'pip install -r requirements-ssh2.txt'\n"
                "2: 'pip install ssh2net[ssh2]'"
            )
            warning = "\n" + msg + "\n" + fix + "\n" + msg
            warnings.warn(warning)
            raise RequirementsNotSatisfied

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
        except self.SSH2AuthenticationException:
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
        except self.SSH2AuthenticationException as exc:
            logging.critical(
                f"Password authentication with host {self.host} failed. Exception: {exc}."
                f"\n\tTrying keyboard interactive auth..."
            )
            try:
                self.session.userauth_keyboardinteractive(  # pylint: disable=E1101
                    self.auth_user, self.auth_password
                )
            except self.SSH2AuthenticationException as exc:
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
