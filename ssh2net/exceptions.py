"""ssh2net.exception"""


class ValidationError(Exception):
    pass


class SetupTimeout(Exception):
    pass


class UnknownPrivLevel(Exception):
    pass
