"""ssh2net.base"""
import ipaddress
import logging
import os
import re
import socket
from typing import Callable, Optional, Union

from ssh2net.channel import SSH2NetChannel
from ssh2net.exceptions import ValidationError
from ssh2net.helper import validate_external_function
from ssh2net.ssh_config import SSH2NetSSHConfig

LOG = logging.getLogger("ssh2net_base")


class SSH2Net(SSH2NetChannel):
    def __init__(
        self,
        setup_host: str = "",
        setup_validate_host: bool = False,
        setup_port: int = 22,
        setup_timeout: int = 5,
        setup_ssh_config_file: Union[str, bool] = False,
        setup_use_paramiko: bool = False,
        session_timeout: int = 5000,
        session_keepalive: bool = False,
        session_keepalive_interval: int = 10,
        session_keepalive_type: str = "network",
        session_keepalive_pattern: str = "\005",
        auth_user: str = "",
        auth_password: Optional[str] = None,
        auth_public_key: Optional[str] = None,
        comms_strip_ansi: bool = False,
        comms_prompt_regex: str = r"^[a-z0-9.\-@()/:]{1,32}[#>$]$",
        comms_operation_timeout: int = 10,
        comms_return_char: str = "\n",
        comms_pre_login_handler: Union[str, Callable] = "",
        comms_disable_paging: Union[str, Callable] = "terminal length 0",
    ):
        r"""
        SSH2Net Object

        SSH2Net Inheritance/Mixin flow:

        SSH2Net <- SSH2NetChannel <- SSH2NetSession <- SSH2NetSocket

        Setup basic parameters required to connect to devices via ssh. Pay extra attention
        to the "comms_prompt_regex" as this is highly critical to this tool working well!

        Args:
            setup_host: ip address or hostname to connect to
            setup_validate_host: whether or not to validate ip address is valid or dns is resolvable
            setup_port: port to open ssh session to
            setup_timeout: timeout in seconds for opening underlying socket to host
            setup_ssh_config_file: ssh config file to use or True to try system default files
            setup_use_paramiko: use paramiko instead of ssh2-python
            session_timeout: time in ms for session read operations; 0 is "forever" and will block
            session_keepalive: whether or not to try to keep session alive
            session_keepalive_interval: interval to use for session keepalives
            session_keepalive_type: network|standard -- "network" sends actual characters over the
                channel as "normal" ssh keepalive doesn't keep sessions open. "standard" sends
                "normal" ssh keepalives via ssh2 library. In both cases a thread is spawned in
                which the keepalives are sent. This introduces a locking mechanism which in
                theory will slow things down slightly, however provides the ability to keep the
                session alive indefinitely. # TODO dont support "normal" via paramiko?
            session_keepalive_pattern: pattern to send to keep network channel alive. Default is
                u"\005" which is equivalent to "ctrl+e". This pattern moves cursor to end of the
                line which should be an innocuous pattern. This will only be entered *if* a lock
                can be acquired.
            auth_user: username to use to connect to host
            auth_password: password to use to connect to host
            auth_public_key: path to ssh public key to use to connect to host
            comms_strip_ansi: whether or not to strip ansi characters from channel
            comms_prompt_regex: regex pattern to use for prompt matching.
                this is the single most important attribute here! if this does not match a prompt,
                ssh2net will not work!
                IMPORTANT: regex search uses multi-line + case insensitive flags. multi-line allows
                for highly reliably matching for prompts after stripping trailing white space,
                case insensitive is just a convenience factor so i can be lazy.
            comms_operation_timeout: timeout in seconds for waiting for channel operations.
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
                - setup_use_paramiko is not a bool
                - session_timeout is not an integer
                - session_keepalive is not a bool
                - session_keepalive_interval is not an integer
                - session_keepalive_type is not "network" or "standard"
                - comms_operation_timeout is not an integer
                - comms_return_char is not a string

        """
        # set a flag to indicate if a shell has been invoked
        self._shell: bool = False

        # setup setup args
        self._setup_setup_args(
            setup_host, setup_validate_host, setup_port, setup_timeout, setup_use_paramiko
        )

        # setup session args
        self._setup_session_args(
            session_timeout,
            session_keepalive,
            session_keepalive_interval,
            session_keepalive_type,
            session_keepalive_pattern,
        )

        # auth setup
        self._setup_auth_args(auth_user, auth_public_key, auth_password)

        # comms setup
        self._setup_comms_args(
            comms_strip_ansi,
            comms_prompt_regex,
            comms_operation_timeout,
            comms_return_char,
            comms_pre_login_handler,
            comms_disable_paging,
        )

        if setup_ssh_config_file:
            if isinstance(setup_ssh_config_file, bool) and setup_ssh_config_file:
                setup_ssh_config_file = ""
            self._setup_ssh_config_args(setup_ssh_config_file)

        LOG.info(f"{str(self)}; {repr(self)}")

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
        Magic bool method for SSH2Net

        Args:
            N/A  # noqa

        Returns:
            bool: True/False if socket is alive or not

        Raises:
            N/A  # noqa

        """
        return self._session_alive()

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
            exception_type: exception type being raised
            exception_value: message from exception being raised
            traceback: traceback from exception being raised

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.close()

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
            LOG.critical(f"Invalid comms_pre_login_handler: {comms_pre_login_handler}")
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
        if comms_disable_paging != "terminal length 0":
            if callable(comms_disable_paging):
                return comms_disable_paging
            ext_func = validate_external_function(comms_disable_paging)
            if ext_func:
                return ext_func
            if isinstance(comms_disable_paging, str):
                return comms_disable_paging
            LOG.critical(f"Invalid comms_disable_paging: {comms_disable_paging}")
            raise ValueError(
                f"{comms_disable_paging} is an invalid comms_disable_paging function, "
                "path to a function, or is not a string."
            )
        return comms_disable_paging

    @staticmethod
    def _invalid_arg_type(target_type, arg_name, arg) -> None:
        """
        Handle invalid argument types for SSH2Net constructor

        Args:
            target_type: expected type of argument
            arg_name: argument name
            arg: value of provided argument

        Returns:
            N/A  # noqa

        Raises:
            TypeError

        """
        LOG.critical(f"Invalid '{arg_name}': {arg}")
        raise TypeError(f"'{arg_name}' must be {target_type}, got: {type(arg)}'")

    def _setup_setup_args(
        self, setup_host, setup_validate_host, setup_port, setup_timeout, setup_use_paramiko
    ) -> None:
        """
        Process and set "setup" args

        Note: setup_ssh_config_file is processed after auth setup

        Args:
            setup_host: ip address or hostname to connect to
            setup_validate_host: whether or not to validate ip address is valid or dns is resolvable
            setup_port: port to open ssh session to
            setup_timeout: timeout in seconds for opening underlying socket to host
            setup_use_paramiko: use paramiko instead of ssh2-python

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.host = setup_host.strip()
        if setup_validate_host:
            self._validate_host()
        self.port = int(setup_port)
        self.setup_timeout = int(setup_timeout)
        if isinstance(setup_use_paramiko, bool):
            self.setup_use_paramiko = setup_use_paramiko
        else:
            self._invalid_arg_type(bool, "setup_use_paramiko", setup_use_paramiko)

    def _setup_session_args(
        self,
        session_timeout,
        session_keepalive,
        session_keepalive_interval,
        session_keepalive_type,
        session_keepalive_pattern,
    ) -> None:
        r"""
        Process and set "session" args

        Args:
            session_timeout: time in ms for session read operations; 0 is "forever" and will block
            session_keepalive: whether or not to try to keep session alive
            session_keepalive_interval: interval to use for session keepalives
            session_keepalive_type: network|standard -- "network" sends actual characters over the
                channel as "normal" ssh keepalive doesn't keep sessions open. "standard" sends
                "normal" ssh keepalives via ssh2 library. In both cases a thread is spawned in
                which the keepalives are sent. This introduces a locking mechanism which in
                theory will slow things down slightly, however provides the ability to keep the
                session alive indefinitely.
            session_keepalive_pattern: pattern to send to keep network channel alive. Default is
                u"\005" which is equivalent to "ctrl+e". This pattern moves cursor to end of the
                line which should be an innocuous pattern. This will only be entered *if* a lock
                can be acquired.

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.session_timeout = int(session_timeout)
        if isinstance(session_keepalive, bool):
            self.session_keepalive = session_keepalive
        else:
            self._invalid_arg_type(bool, "session_keepalive", session_keepalive)
        self.session_keepalive_interval = int(session_keepalive_interval)
        if session_keepalive_type not in ["network", "standard"]:
            raise ValueError(
                f"{session_keepalive_type} is an invalid session_keepalive_type; must be "
                "'network' or 'standard'."
            )
        self.session_keepalive_type = session_keepalive_type
        self.session_keepalive_pattern = session_keepalive_pattern

    def _setup_auth_args(self, auth_user, auth_public_key, auth_password) -> None:
        """
        Process and set "auth" args

        Args:
            auth_user: username to use to connect to host
            auth_password: password to use to connect to host
            auth_public_key: path to ssh public key to use to connect to host

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.auth_user = auth_user.strip()
        if auth_public_key:
            self.auth_public_key = os.path.expanduser(auth_public_key.strip().encode())
        else:
            self.auth_public_key = auth_public_key
        if auth_password:
            self.auth_password = auth_password.strip()
        else:
            self.auth_password = auth_password

    def _setup_comms_args(
        self,
        comms_strip_ansi,
        comms_prompt_regex,
        comms_operation_timeout,
        comms_return_char,
        comms_pre_login_handler,
        comms_disable_paging,
    ):
        """
        Process and set "comms" args

        Args:
            comms_strip_ansi: whether or not to strip ansi characters from channel
            comms_prompt_regex: regex pattern to use for prompt matching.
                this is the single most important attribute here! if this does not match a prompt,
                ssh2net will not work!
                IMPORTANT: regex search uses multi-line + case insensitive flags. multi-line allows
                for highly reliably matching for prompts after stripping trailing white space,
                case insensitive is just a convenience factor so i can be lazy.
            comms_operation_timeout: timeout in seconds for waiting for channel operations.
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
            N/A  # noqa

        """
        if isinstance(comms_strip_ansi, bool):
            self.comms_strip_ansi = comms_strip_ansi
        else:
            self._invalid_arg_type(bool, "comms_strip_ansi", comms_strip_ansi)

        # try to compile prompt to raise TypeError before opening any connections
        re.compile(comms_prompt_regex, flags=re.M | re.I)
        self.comms_prompt_regex = comms_prompt_regex
        self.comms_operation_timeout = int(comms_operation_timeout)

        # validate that the return character set is a string
        # do this to ensure provided value is a string; this prevents an int being cast to string
        # making it look like things are ok
        if isinstance(comms_return_char, str):
            self.comms_return_char = comms_return_char
        else:
            self._invalid_arg_type(str, "comms_return_char", comms_return_char)
        self.comms_pre_login_handler = self._set_comms_pre_login_handler(comms_pre_login_handler)
        self.comms_disable_paging = self._set_comms_disable_paging(comms_disable_paging)

    def _setup_ssh_config_args(self, setup_ssh_config_file: Union[str, bool]) -> None:
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
            LOG.info(f"Failed to validate host {self.host} as an ip address")
        try:
            socket.gethostbyname(self.host)
            return
        except socket.gaierror:
            LOG.info(f"Failed to validate host {self.host} as a resolvable dns name")
        raise ValidationError(f"Host {self.host} is not an IP or resolvable DNS name.")
