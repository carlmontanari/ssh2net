"""ssh2net.session"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from threading import Lock
import time


from ssh2net.channel import SSH2NetChannel
from ssh2net.session_miko import SSH2NetSessionParamiko
from ssh2net.session_ssh2 import SSH2NetSessionSSH2


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
            return self._session_check_authenticated()
        except AttributeError:
            # session never created yet; there may be other exceptions we need to catch here
            logging.debug(f"Session to host {self.host} has never been created")
            return False

    def _keepalive_thread(self) -> None:
        """
        Attempt to keep sessions alive.

        In the case of "networking" equipment this will try to acquire a session lock and send an
        innocuous character -- such as CTRL+E -- to keep the device "exec-timeout" from expiring.

        For "normal" devices that allow for a standard ssh keepalive, this thread will simply use
        those mechanisms to maintain the session. This will likely break (for "normal" devices) if
        using paramiko for the underlying driver, but has not been tested yet!

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
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
        """
        Spawn keepalive thread for ssh session

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if not self.session_keepalive:
            return
        pool = ThreadPoolExecutor()
        pool.submit(self._keepalive_thread)

    def _acquire_session_lock(self) -> None:
        """
        Attempt to acquire session lock

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
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
        if self.setup_use_paramiko is False:
            ssh2_session_obj = SSH2NetSessionSSH2(self)
            self._session_open_connect = (
                ssh2_session_obj._session_open_connect  # pylint: disable=W0212
            )
            self._session_public_key_auth = (
                ssh2_session_obj._session_public_key_auth  # pylint: disable=W0212
            )
            self._session_password_auth = (
                ssh2_session_obj._session_password_auth  # pylint: disable=W0212
            )
            self._channel_open_driver = (
                ssh2_session_obj._channel_open_driver  # pylint: disable=W0212
            )
            self._channel_invoke_shell = (
                ssh2_session_obj._channel_invoke_shell  # pylint: disable=W0212
            )
        else:
            miko_sesion_obj = SSH2NetSessionParamiko(self)
            self._session_open_connect = (
                miko_sesion_obj._session_open_connect  # pylint: disable=W0212
            )
            self._session_public_key_auth = (
                miko_sesion_obj._session_public_key_auth  # pylint: disable=W0212
            )
            self._session_password_auth = (
                miko_sesion_obj._session_password_auth  # pylint: disable=W0212
            )
            self._channel_open_driver = (
                miko_sesion_obj._channel_open_driver  # pylint: disable=W0212
            )
            self._channel_invoke_shell = (
                miko_sesion_obj._channel_invoke_shell  # pylint: disable=W0212
            )

        if not self._socket_alive():
            self._socket_open()
        if not self._session_alive():
            self._session_open_connect()

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

    def _session_check_authenticated(self) -> bool:
        """
        Check if session is authenticated

        Args:
            N/A  # noqa

        Returns:
            bool: True/False for session authenticated

        Raises:
            N/A  # noqa

        """
        if self.setup_use_paramiko is False:
            return self.session.userauth_authenticated()
        return self.session.is_authenticated()

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
        if self.session is not None:  # pylint: disable=E0203
            if self.setup_use_paramiko:
                self.session.close()  # pylint: disable=E0203
            else:
                self.session.disconnect()  # pylint: disable=E0203
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
            self._channel_open_driver()

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
        if self.channel is not None:  # pylint: disable=E0203
            self.channel.close  # noqa
            self.channel = None
            logging.debug(f"Channel to host {self.host} closed")
