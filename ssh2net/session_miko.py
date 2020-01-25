"""ssh2net.session_miko"""
import logging
import time
import warnings

from ssh2net.exceptions import AuthenticationFailed, RequirementsNotSatisfied


class SSH2NetSessionParamiko:
    def __init__(self, p_self):
        """
        SSH2NetSessionParamiko Object

        This object, through composition, allows for using Paramiko as the underlying "driver"
        for SSH2Net instead of the default "ssh2-python". Paramiko will be ever so slightly
        slower but as you will most likely be I/O constrained it shouldn't matter! "ssh2-python" as
        of 20 October 2019 has a bug preventing keyboard interactive authentication from working as
        desired; this is the reason Paramiko is in here now!

        Args:
            p_self: SSH2Net object

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        # due to somewhat shitty composition and problematic multiple inheritance (how do i know to
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
        Perform session handshake for paramiko (instead of default ssh2-python)

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            RequirementsNotSatisfied: if paramiko is not installed
            Exception: catch all for unknown exceptions during session handshake

        """
        try:
            from paramiko import Transport  # pylint: disable=C0415
            from paramiko.ssh_exception import (  # pylint: disable=C0415
                AuthenticationException,
                SSHException,
            )

            self.ParamikoAuthenticationException = AuthenticationException
            self.session_driver_timeout_exception = SSHException
        except ModuleNotFoundError as exc:
            err = f"Module '{exc.name}' not installed!"
            msg = f"***** {err} {'*' * (80 - len(err))}"
            fix = (
                f"To resolve this issue, install '{exc.name}'. You can do this in one of the "
                "following ways:\n"
                "1: 'pip install -r requirements-paramiko.txt'\n"
                "2: 'pip install ssh2net[paramiko]'"
            )
            warning = "\n" + msg + "\n" + fix + "\n" + msg
            warnings.warn(warning)
            raise RequirementsNotSatisfied
        try:
            self.session = Transport(self.sock)
            self.session.start_client()
            self.session.set_timeout = self._set_timeout
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
            self.session.auth_publickey(self.auth_user, self.auth_public_key)
        except self.ParamikoAuthenticationException:
            logging.critical(f"Public key authentication with host {self.host} failed.")
        except Exception as exc:
            logging.critical(
                "Unknown error occurred during public key authentication with host "
                f"{self.host}; Exception: {exc}"
            )
            raise exc

    def _session_password_auth(self) -> None:
        """
        Perform password or keyboard interactive based auth on SSH2NetSession

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            AuthenticationFailed: if authentication fails
            Exception: catch all for unknown other exceptions

        """
        try:
            self.session.auth_password(self.auth_user, self.auth_password)
        except self.ParamikoAuthenticationException as exc:
            logging.critical(
                f"Password authentication with host {self.host} failed. Exception: {exc}."
                "\n\tNote: Paramiko automatically attempts both standard auth as well as keyboard "
                "interactive auth. Paramiko exception about bad auth type may be misleading!"
            )
            raise AuthenticationFailed
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
        self.channel.get_pty()
        logging.debug(f"Channel to host {self.host} opened")

    def _channel_invoke_shell(self) -> None:
        """
        Invoke shell on channel

        Additionally, this "re-points" some ssh2net method calls to the appropriate paramiko
        methods. This happens as ssh2net is primarily built on "ssh2-python" and there is not
        full parity between paramiko/ssh2-python.

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self._shell = True
        self.channel.invoke_shell()
        self.channel.read = self._paramiko_read_channel
        self.channel.write = self.channel.sendall
        self.session.set_blocking = self._set_blocking
        self.channel.flush = self._flush

    def _paramiko_read_channel(self):
        """
        Patch channel.read method for paramiko driver

        "ssh2-python" returns a tuple of bytes and data, "paramiko" simply returns the data
        from the channel, patch this for parity with "ssh2-python".

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        channel_read = self.channel.recv(1024)
        return None, channel_read

    def _flush(self):
        """
        Patch a "flush" method for paramiko driver

        Need to investigate this further for two things:
            1) is "flush" even necessary when using ssh2-python driver?
            2) if it is necessary, is there a combination of reads/writes that would implement
                this in a sane fashion for paramiko

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        while True:
            time.sleep(0.1)
            if self.channel.recv_ready():
                self._paramiko_read_channel()
            else:
                return

    def _set_blocking(self, blocking) -> None:
        """
        Set blocking and timeout values for underlying Paramiko driver

        When setting paramiko to non-blocking paramiko resets the timeout to 0, so we also reset
        timeout whenever we set blocking. Convert milliseconds to seconds for Paramiko.

        Args:
            blocking:

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.channel.setblocking(blocking)
        self.channel.settimeout(self.session_timeout / 1000)

    def _set_timeout(self, timeout: int) -> None:
        """
        Set timeout for Paramiko driver.

        Convert milliseconds to seconds for Paramiko.

        Args:
            timeout: timeout in milliseconds

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.channel.settimeout(timeout / 1000)
