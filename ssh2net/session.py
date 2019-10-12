"""ssh2net.session"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from threading import Lock
import time

from ssh2.session import Session
from ssh2.exceptions import AuthenticationError

from ssh2net.channel import SSH2NetChannel


class SSH2NetSession(SSH2NetChannel):
    def _session_alive(self):
        """
        Check if session is alive and authenticated

        Args:
            N/A  # noqa

        Returns:
            bool True/False session is alive and authenticated

        Raises:
            N/A  # noqa

        """
        try:
            # if authenticated we can assume session is good to go
            return self.session.userauth_authenticated()
        except AttributeError:
            # session never created yet; there may be other exceptions we need to catch here
            logging.debug(f"Session to host {self.host} has never been created")
            return False

    def _keepalive_thread(self) -> None:
        lock_counter = 0
        last_keepalive = datetime.now()
        if self.session_keepalive_type == "network":
            while True:
                if not self._session_alive():
                    return
                diff = datetime.now() - last_keepalive
                if diff.seconds >= self.session_keepalive_interval:
                    if not self.session_lock.locked():
                        lock_counter = 0
                        self.session_lock.acquire_lock()
                        self.channel.write(self.session_keepalive_pattern)
                        self.session_lock.release_lock()
                        last_keepalive = datetime.now()
                    else:
                        lock_counter += 1
                        if lock_counter >= 3:
                            print(
                                f"Keepalive thread missed {lock_counter} consecutive keepalives..."
                            )
                time.sleep(self.session_keepalive_interval / 10)
        elif self.session_keepalive_type == "standard":
            self.session.keepalive_config(
                want_reply=False, interval=self.session_keepalive_interval
            )
            while True:
                if not self._session_alive():
                    return
                self.session.keepalive_send()
                time.sleep(self.session_keepalive_interval / 10)

    def _session_keepalive(self) -> None:
        if not self.session_keepalive:
            return
        pool = ThreadPoolExecutor()
        pool.submit(self._keepalive_thread)

    def _acquire_session_lock(self) -> None:
        while True:
            if not self.session_lock.locked():
                self.session_lock.acquire_lock()
                return

    def _session_open(self) -> None:
        """
        Open SSH session

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if not self._socket_alive():
            self._socket_open()
        if not self._session_alive():
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

        logging.debug(f"Session to host {self.host} opened")
        self.session_lock = Lock()
        if self.auth_public_key:
            self._session_public_key_auth()
            if self._session_alive():
                return
        if self.auth_password:
            self._session_password_auth()
            if self._session_alive():
                return

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
            AuthenticationError: if authentication fails
            Exception: catch all for unknown other exceptions

        """
        try:
            self.session.userauth_password(self.auth_user, self.auth_password)
        except AuthenticationError as exc:
            logging.critical(
                f"Password authentication with host {self.host} failed. "
                f"Exception: {exc}. Trying keyboard interactive auth..."
            )
            try:
                self.session.userauth_keyboardinteractive(self.auth_user, self.auth_password)
            except AuthenticationError as exc:
                logging.critical(
                    f"Keyboard interactive authentication with host {self.host} failed. "
                    f"Exception: {exc}."
                )
                raise exc
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

    def _session_close(self) -> None:
        """
        Close SSH SSH2NetSession

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if self.session is not None:
            self.session.disconnect()
            self.session = None
            logging.debug(f"Session to host {self.host} closed")

    """ channel setup """  # noqa

    def _channel_alive(self) -> bool:
        """
        Check if channel is alive

        Args:
            N/A  # noqa

        Returns:
            bool True/False channel is alive

        Raises:
            N/A  # noqa

        """
        try:
            if self.channel:
                return True
        except AttributeError:
            # channel not created, or closed
            logging.debug(f"Channel to host {self.host} has never been created")
            return False
        return False

    def _channel_open(self) -> None:
        """
        Open channel

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if not self._session_alive():
            self._session_open()
        if not self._channel_alive():
            self.channel = self.session.open_session()
            self.channel.pty()
            logging.debug(f"Channel to host {self.host} opened")

    def _channel_close(self) -> None:
        """
        Close channel

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if self.channel is not None:
            self.channel.close  # noqa
            self.channel = None
            logging.debug(f"Channel to host {self.host} closed")

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
