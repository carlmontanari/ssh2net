"""ssh2net.session"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from typing import Callable, Optional, Union

from ssh2net.session_miko import SSH2NetSessionParamiko
from ssh2net.session_ssh2 import SSH2NetSessionSSH2
from ssh2net.socket import SSH2NetSocket
from ssh2net.type_helper import DummyChannel, DummySession

TRANSPORT_CLASS_SELECTOR = {True: SSH2NetSessionParamiko, False: SSH2NetSessionSSH2}

LOG = logging.getLogger("ssh2net_session")


class SSH2NetSession(SSH2NetSocket):
    """
    SSH2NetSession

    SSH2NetBase <- SSH2NetChannel <- SSH2NetSession <- SSH2NetSocket

    SSH2NetSession is responsible for handling the actual SSH session that gets built atop the
    socket connection. SSH2NetSession should not care about what is providing the session. At time
    of writing the session can be provided by ssh2-python or paramiko. The session provided must
    provide the following methods:

        is_authenticated:
            TODO

        userauth_authenticated:
            TODO

        keepalive_config:
            TODO

        keepalive_send:
            TODO

        close:
            TODO

        disconnect:
            TODO

        set_timeout:
            TODO

    Arguments are type hinted here for linting, these should all come from the SSH2Net child class.
    ssh2net uses a mixin type structure to divide each logical component of the overall ssh2net
    object into its own class. Because of the mixin structure there are no init methods in the
    Channel, Session, or Socket classes. In order to appease mypy and ensure that ssh2net is typed
    reasonably well the typing information for these classes are done at the class level as found
    here.

    """

    host: str
    setup_validate_host: bool
    setup_port: int
    setup_timeout: int
    setup_ssh_config_file: Union[str, bool]
    setup_use_paramiko: bool
    session_timeout: int
    session_keepalive: bool
    session_keepalive_interval: int
    session_keepalive_type: str
    session_keepalive_pattern: str
    auth_user: str
    auth_password: Optional[str]
    auth_public_key: Optional[str]
    comms_strip_ansi: bool
    comms_prompt_regex: str
    comms_operation_timeout: int
    comms_return_char: str
    comms_pre_login_handler: Callable
    comms_disable_paging: Union[str, Callable]

    _shell: bool
    session: DummySession
    channel: DummyChannel

    def __bool__(self):
        """
        Magic bool method for SSH2NetSession

        Args:
            N/A  # noqa

        Returns:
            bool: True/False if session is alive or not

        Raises:
            N/A  # noqa

        """
        return self._session_alive()

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
                        self.session_lock.acquire()
                        self.channel.write(self.session_keepalive_pattern)
                        self.session_lock.release()
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
                self.session_lock.acquire()
                return

    def _session_open(self) -> None:
        """
        Open SSH session

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            TypeError: if for some reason the desired driver can't be loaded

        """
        # setup the socket prior to creating composite transport class so we can point to it in the
        # child class
        if not self._socket_alive():
            self._socket_open()

        driver_session: Optional[Callable] = TRANSPORT_CLASS_SELECTOR.get(
            self.setup_use_paramiko, None
        )
        if not driver_session:
            raise TypeError

        driver_session_obj = driver_session(self)

        # assign methods/attributes from transport class to this base class
        self._session_open_connect = (
            driver_session_obj._session_open_connect  # pylint: disable=W0212
        )
        self._session_public_key_auth = (
            driver_session_obj._session_public_key_auth  # pylint: disable=W0212
        )
        self._session_password_auth = (
            driver_session_obj._session_password_auth  # pylint: disable=W0212
        )
        self._channel_open_driver = driver_session_obj._channel_open_driver  # pylint: disable=W0212
        self._channel_invoke_shell = (
            driver_session_obj._channel_invoke_shell  # pylint: disable=W0212
        )

        if not self._session_alive():
            self._session_open_connect()
            self.session_driver_timeout_exception = (
                driver_session_obj.session_driver_timeout_exception
            )

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

    def _open_and_execute(self, command: str) -> bytes:
        """
        Open ssh channel and execute a command; closes channel when done.

        "one time use" method -- best for running one command then moving on; otherwise
        use "open_shell" instead, though this will likely be substantially faster for "single"
        operations.

        Args:
            command: string input to write to channel

        Returns:
            result: output from command sent over the channel

        Raises:
            N/A  # noqa

        """
        # import here so ssh2 is not required if using different ssh driver
        from ssh2.exceptions import SocketRecvError  # noqa

        LOG.info(f"Attempting to open channel for command execution")
        if self._shell:
            self._channel_close()
        self._channel_open()
        output = b""
        channel_buff = 1
        LOG.debug(f"Channel open, executing command: {command}")
        self.channel.execute(command)
        while channel_buff > 0:
            try:
                channel_buff, data = self.channel.read()
                output += data
            except SocketRecvError:
                break
        self.close()
        LOG.info(f"Command executed, channel closed")
        return output

    def _open_shell(self) -> None:
        """
        Open and prepare interactive SSH shell

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        LOG.info(f"Attempting to open interactive shell")
        # open the channel itself
        self._channel_open()
        # invoke a shell on the channel
        self._channel_invoke_shell()
        self._session_keepalive()
        LOG.info("Interactive shell opened")

    def close(self) -> None:
        """
        Fully close socket, session, and channel

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self._channel_close()
        self._session_close()
        self._socket_close()
        LOG.info(f"{str(self)}; Closed")
