"""ssh2net.exceptions"""


class ValidationError(Exception):
    pass


class RequirementsNotSatisfied(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


class SetupTimeout(Exception):
    pass


class UnknownPrivLevel(Exception):
    pass
