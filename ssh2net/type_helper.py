"""ssh2net.type_helper"""


class DummyChannel:
    """Dummy channel object for typing without needing to import ssh2-python or paramiko"""

    def flush(self):
        """Flush method for DummyChannel"""

    def read(self):
        """Read method for DummyChannel"""

    def write(self, channel_input: str):
        """
        Write method for DummyChannel

        Args:
            channel_input: string input to send to channel

        """

    def execute(self, channel_input: str):
        """
        Execute method for DummyChannel

        Does not apply for paramiko

        Args:
            channel_input: string input to send to channel

        """

    def close(self):
        """Close method for DummyChannel"""


class DummySession:
    """Dummy session object for typing without needing to import ssh2-python or paramiko"""

    def is_authenticated(self):
        """User auth verification method for DummySession"""

    def userauth_authenticated(self):
        """User auth verification method for DummySession"""

    def keepalive_config(self, want_reply: bool, interval: int):
        """
        Keepalive configuration method for DummySession

        Args:
            want_reply: True/False want keepalive reply
            interval: keepalive interval

        """

    def keepalive_send(self):
        """Send keepalive method for DummySession"""

    def close(self):
        """Close method for DummySession"""

    def disconnect(self):
        """Disconnect method for DummySession"""

    def set_timeout(self, timeout: int):
        """
        Set timeout method for DummySession

        Args:
            timeout: timeout value

        """
