"""ssh2net.base"""
import ipaddress
import logging
import os
import re
import socket
from typing import Callable, Optional, Union

from ssh2net.channel import SSH2NetChannel
from ssh2net.exceptions import ValidationError, SetupTimeout
from ssh2net.helper import validate_external_function
from ssh2net.session import SSH2NetSession
from ssh2net.ssh_config import SSH2NetSSHConfig


session_log = logging.getLogger("ssh2net_session")


class SSH2Net(SSH2NetChannel, SSH2NetSession):
    def __init__(
        self,
        setup_host: str = "",
        setup_validate_host: Optional[bool] = False,
        setup_port: Optional[int] = 22,
        setup_timeout: Optional[int] = 5,
        setup_ssh_config_file: Optional[Union[str, bool]] = False,
        session_keepalive: Optional[bool] = False,
        session_keepalive_interval: Optional[int] = 10,
        session_timeout: Optional[int] = 5000,
        auth_user: str = "",
        auth_password: Optional[Union[str]] = None,
        auth_public_key: Optional[Union[str]] = None,
        comms_prompt_regex: Optional[str] = r"^[a-z0-9.\-@()/:]{1,32}[#>$]$",
        comms_prompt_timeout: Optional[int] = 10,
        comms_return_char: Optional[str] = "\n",
        comms_pre_login_handler: Optional[Union[str, Callable]] = "",
        comms_disable_paging: Optional[Union[str, Callable]] = "terminal length 0",
    ):
        r"""
        Initialize SSH2Net Object

        Setup basic parameters required to connect to devices via ssh. Pay extra attention
        to the "comms_prompt_regex" as this is highly critical to this tool working well!

        Args:
            setup_host: ip address or hostname to connect to
            setup_validate_host: whether or not to validate ip address is valid or dns is resolvable
            setup_port: port to open ssh session to
            setup_timeout: timeout in seconds for opening underlying socket to host
            setup_ssh_config_file: ssh config file to use or True to try system default files
            session_keepalive: FUTURE USE: whether or not to try to keep session alive
            session_keepalive_interval: FUTURE USE: interval to use for session keepalives
            session_timeout: time in ms for session read operations; 0 is "forever" and will block
            auth_user: username to use to connect to host
            auth_password: password to use to connect to host
            auth_public_key: path to ssh public key to use to connect to host
            comms_prompt_regex: regex pattern to use for prompt matching.
                this is the single most important attribute here! if this does not match a prompt,
                ssh2net will not work!
                IMPORTANT: regex search uses multiline and case insensetive flags. multiline allows
                for highly reliably matching for prompts after stripping trailling white space,
                case insensetive is just a convenience factor so i can be lazy.
            comms_prompt_timeout: timeout in seconds for waiting for channel operations.
                this is NOT the "read" timeout. this is the timeout for the entire operation
                sent to send_inputs/send_inputs_interact
            comms_return_char: character to use to send returns to host
            comms_pre_login_handler: callable or string that resolves to an importable function to
                handle pre-login (pre disable paging) operations
            comms_disable_paging: callable, string that resolves to an importable function, or
                string to send to device to disable paging

        Returns:
            N/A  # noqa

        Raises:
            ValueError: in the following situations:
                - setup_port is not an integer
                - setup_timeout is not an integer
                - session_keepalive is not an integer
                - session_keepalive_interval is not an integer
                - session_timeout is not an integer
                - comms_prompt_timeout is not an integer
                - comms_return_char is not a string

        """
        # set a flag to indicate if a shell has been invoked
        self._shell: bool = False

        # pre socket setup
        self.host = setup_host.strip()
        if setup_validate_host:
            self._validate_host()
        self.port = int(setup_port)

        # socket setup
        self.setup_timeout = int(setup_timeout)

        # session setup
        self.session_keepalive = int(session_keepalive)
        self.session_keepalive_interval = int(session_keepalive_interval)
        self.session_timeout = int(session_timeout)

        # auth setup
        self.auth_user = auth_user.strip()
        if auth_public_key:
            self.auth_public_key = os.path.expanduser(auth_public_key.strip().encode())
        else:
            self.auth_public_key = auth_public_key
        if auth_password:
            self.auth_password = auth_password.strip()
        else:
            self.auth_password = auth_password

        # comms setup
        # try to compile prompt to raise TypeError before opening any connections
        re.compile(comms_prompt_regex, flags=re.M | re.I)
        self.comms_prompt_regex = comms_prompt_regex
        self.comms_prompt_timeout = int(comms_prompt_timeout)

        # validate that the return character set is a string
        # do this to ensure provided value is a string; this prevents an int being cast to string
        # making it look like things are ok
        if isinstance(comms_return_char, str):
            self.comms_return_char = comms_return_char
        else:
            session_log.critical(f"Invalid comms_return_char: {comms_return_char}")
            raise ValueError(
                f"{comms_return_char} is an invalid comms_return_char; must be string."
            )

        self.comms_pre_login_handler = self._set_comms_pre_login_handler(comms_pre_login_handler)
        self.comms_disable_paging = self._set_comms_disable_paging(comms_disable_paging)

        if setup_ssh_config_file:
            if isinstance(setup_ssh_config_file, bool) and setup_ssh_config_file:
                setup_ssh_config_file = ""
            self._setup_ssh_config_args(setup_ssh_config_file)

        session_log.info(f"{str(self)}; {repr(self)}")

    def __enter__(self):
        """
        Enter method for context manager

        Args:
            N/A  # noqa

        Returns:
            self: instance of self

        Raises:
            N/A  # noqa

        """
        self.open_shell()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Exit method to cleanup for context manager

        Args:
            exception_type: execption type being raised
            exception_value: message from exception being raised
            traceback: traceback from exception being raised

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.close()

    def __str__(self):
        """
        Magic str method for SSH2Net class

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        return f"SSH2Net Connection Object for host {self.host}"

    def __repr__(self):
        """
        Magic repr method for SSH2Net class

        Args:
            N/A  # noqa

        Returns:
            repr: repr for class object

        Raises:
            N/A  # noqa

        """
        class_dict = self.__dict__.copy()
        class_dict["auth_password"] = "********"
        return f"SSH2Net {class_dict}"

    def __bool__(self):
        """
        Magic bool method based on result of session_alive

        Args:
            N/A  # noqa

        Returns:
            bool: True/False if session is alive or not

        Raises:
            N/A  # noqa

        """
        return self._session_alive()

    @staticmethod
    def _set_comms_pre_login_handler(
        comms_pre_login_handler: Union[Callable, str]
    ) -> Union[Callable, str]:
        """
        Return comms_pre_login_handler argument

        Args:
            comms_pre_login_handler: callable function, or string representing a path to
                a callable

        Returns:
            comms_pre_login_handler: callable or default empty string value

        Raises:
            ValueError: if provided string does not result in a callable

        """
        if comms_pre_login_handler:
            if callable(comms_pre_login_handler):
                return comms_pre_login_handler
            ext_func = validate_external_function(comms_pre_login_handler)
            if ext_func:
                return ext_func
            session_log.critical(f"Invalid comms_pre_login_handler: {comms_pre_login_handler}")
            raise ValueError(
                f"{comms_pre_login_handler} is an invalid comms_pre_login_handler function "
                "or path to a function."
            )
        return comms_pre_login_handler

    @staticmethod
    def _set_comms_disable_paging(
        comms_disable_paging: Union[Callable, str]
    ) -> Union[Callable, str]:
        """
        Return comms_disable_paging argument

        Args:
            comms_disable_paging: callable function, string representing a path to
                a callable, or a string to send to device to disable paging

        Returns:
            comms_disable_paging: callable or string to use to disable paging

        Raises:
            ValueError: if provided string does not result in a callable

        """
        if comms_disable_paging != "term length 0":
            if callable(comms_disable_paging):
                return comms_disable_paging
            ext_func = validate_external_function(comms_disable_paging)
            if ext_func:
                return ext_func
            if isinstance(comms_disable_paging, str):
                return comms_disable_paging
            session_log.critical(f"Invalid comms_disable_paging: {comms_disable_paging}")
            raise ValueError(
                f"{comms_disable_paging} is an invalid comms_disable_paging function, "
                "path to a function, or is not a string."
            )
        return comms_disable_paging

    def _setup_ssh_config_args(self, setup_ssh_config_file):
        """
        Set any args from ssh config file to override existing settings

        Args:
            setup_ssh_config_file: string of path to ssh config file, or bool True

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        ssh_config = SSH2NetSSHConfig(setup_ssh_config_file)
        host_config = ssh_config.lookup(self.host)
        if host_config.port:
            self.setup_port = host_config.port
        if host_config.user:
            self.auth_user = host_config.user
        if host_config.identity_file:
            self.auth_public_key = os.path.expanduser(host_config.identity_file.strip().encode())

    """ pre socket setup """  # noqa

    def _validate_host(self) -> None:
        """
        Validate host is valid IP or resolvable DNS name

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            ValidationError: if host is invalid IP and is non resolvable

        """
        try:
            ipaddress.ip_address(self.host)
            return
        except ValueError:
            session_log.info(f"Failed to validate host {self.host} as an ip address")
        try:
            socket.gethostbyname(self.host)
            return
        except socket.gaierror:
            session_log.info(f"Failed to validate host {self.host} as a resovable dns name")
        raise ValidationError(f"Host {self.host} is not an IP or resolvable DNS name.")

    """ socket setup """  # noqa

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
            session_log.debug(f"Socket to host {self.host} is not alive")
            return False
        except AttributeError:
            # socket never created yet
            session_log.debug(f"Socket to host {self.host} has never been created")
            return False

    def _socket_open(self) -> None:
        """
        Open underyling socket

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
                session_log.critical(
                    f"Timed out trying to open socket to {self.host} on port {self.port}"
                )
                raise SetupTimeout(
                    f"Timed out trying to open socket to {self.host} on port {self.port}"
                )
            session_log.debug(f"Socket to host {self.host} opened")

    def _socket_close(self) -> None:
        """
        Close underyling socket

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if self._socket_alive():
            self.sock.close()
            session_log.debug(f"Socket to host {self.host} closed")

    def close(self) -> None:
        """
        Fully close scoket, session, and channel

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
        session_log.info(f"{str(self)}; Closed")
