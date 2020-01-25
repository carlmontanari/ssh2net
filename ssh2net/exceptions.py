"""ssh2net.exceptions"""


class ValidationError(Exception):
    """Exception for any argument validation"""


class RequirementsNotSatisfied(Exception):
    """Exception for any requirements not satisfied (missing dependencies)"""


class AuthenticationFailed(Exception):
    """Exception for any authentication failures"""


class SetupTimeout(Exception):
    """Exception for any timeout setting up socket"""


class UnknownPrivLevel(Exception):
    """Exception for encountering unknown privilege level"""


class CouldNotAcquirePrivLevel(Exception):
    """Exception for failure to acquire desired privilege level"""
