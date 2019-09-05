"""ssh2net.session"""
import logging

from ssh2.session import Session
from ssh2.exceptions import AuthenticationError


class SSH2NetSession:
    def _session_alive(self):
        """
        Check if session is alive and authenticated

        Args:
            N/A

        Returns:
            bool True/False session is alive and authenticated

        Raises:
            N/A

        """
        try:
            # if authenticated we can assume session is good to go
            return self.session.userauth_authenticated()
        except AttributeError:
            # session never created yet; there may be other exceptions we need to catch here
            logging.debug(f"Session to host {self.host} has never been created")
            return False

    def _session_open(self) -> None:
        """
        Open SSH session

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A

        """
        if not self._socket_alive():
            self._socket_open()
        if not self._session_alive():
            self.session = Session()
            if self.session_keepalive:
                self.session.keepalive_config(False, self.session_keepalive_interval)
            if self.session_timeout:
                self.session.set_timeout(self.session_timeout)
            try:
                self.session.handshake(self.sock)
            except Exception as e:
                logging.critical(
                    f"Failed to complete handshake with host {self.host}; " f"Exception: {e}"
                )
                raise e
        # authenticate -- think about preferred order: key -> pass -> interactive?
        logging.debug(f"Session to host {self.host} opened")
        self._session_password_auth()

    def _session_password_auth(self) -> None:
        """
        Perform password based auth on SSH2NetSession

        Args:
            N/A

        Returns:
            N/A

        Raises:
            AuthenticationError: if authentication fails
            Exception: catch all for uknown other exceptions

        """
        try:
            self.session.userauth_password(self.auth_user, self.auth_password)
        except AuthenticationError as e:
            logging.critical(
                f"Password authentication with host {self.host} failed. "
                f"Exception: {e}. Trying keyboard interactive auth..."
            )
            try:
                self.session.userauth_keyboardinteractive(self.auth_user, self.auth_password)
            except AuthenticationError as e:
                raise e
            except Exception as e:
                raise e
        except Exception as e:
            logging.critical(
                "Unkown error occured during password authentication with host "
                f"{self.host}; Exception: {e}"
            )
            raise e

    def _session_close(self) -> None:
        """
        Close SSH SSH2NetSession

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A

        """
        if self.session is not None:
            self.session.disconnect()
            self.session = None
            logging.debug(f"Session to host {self.host} closed")

    """ channel setup """

    def _channel_alive(self) -> bool:
        """
        Check if channel is alive

        Args:
            N/A

        Returns:
            bool True/False channel is alive

        Raises:
            N/A

        """
        try:
            if self.channel:
                return True
        except AttributeError:
            # channel not created or closed
            logging.debug(f"Channel to host {self.host} has never been created")
            return False
        return False

    def _channel_open(self) -> None:
        """
        Open channel

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A

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
            N/A

        Returns:
            N/A

        Raises:
            N/A

        """
        if self.channel is not None:
            self.channel.close
            self.channel = None
            logging.debug(f"Channel to host {self.host} closed")

    def _channel_invoke_shell(self) -> None:
        """
        Invoke shell on channel

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A

        """
        self._shell = True
        self.channel.shell()
