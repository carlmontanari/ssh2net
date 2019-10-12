"""ssh2net.decorators"""
import logging
import signal
import time


channel_log = logging.getLogger("ssh2net_channel")


def operation_timeout(attribute):
    """
    Decorate an "operation" -- raises exception if the operation timeout is exceeded

    This decorator wraps an entire "operation" -- in other words for each send_input or
    send_inputs_interact this decorator wraps that entire operation. The `comms_operation_timeout`
    value governs this timeout decorator -- and as such it should always be larger than the base
    `session_timeout` argument plus the amount of time that `channel_timeout` decorator will delay
    while retrying the read operation.

    Args:
        attribute: attribute to inspect in class (to set timeout duration)

    Returns:
        decorate: wrapped function

    Raises:
        TimeoutError: if timeout exceeded

    """

    def _raise_exception(signum, frame):
        raise TimeoutError

    def decorate(wrapped_func):
        def timeout_wrapper(self, *args, **kwargs):
            timeout_duration = getattr(self, attribute)
            if not timeout_duration:
                return wrapped_func
            old = signal.signal(signal.SIGALRM, _raise_exception)
            signal.setitimer(signal.ITIMER_REAL, timeout_duration)
            try:
                return wrapped_func(self, *args, **kwargs)
            finally:
                if timeout_duration:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, old)

        return timeout_wrapper

    return decorate


def channel_timeout(exception_to_check, attempts=5, starting_delay=0.1, backoff=2):
    """
    Decorate read operations; basic backoff timer to try to read channel for reasonable time

    This decorator wraps individual read operations. If/when the read operation times out
    (timeout configured by `session_timeout`), run a basic backoff process retrying five times

    Args:
        exception_to_check: Exception to handle; basically if this exception is seen, try again
        attempts: number of attempts to make to retry
        starting_delay: initial backoff delay
        backoff: backoff multiplier

    Returns:
        decorate: wrapped function

    Raises:
        N/A  # noqa

    """

    def decorate(wrapped_func):
        def retry_wrapper(self, *args, **kwargs):
            attempt, delay = attempts, starting_delay
            while attempt > 1:
                try:
                    return wrapped_func(self, *args, **kwargs)
                except exception_to_check:
                    channel_log.info(f"Retrying read operation in {delay} seconds...")
                    time.sleep(delay)
                    attempt -= 1
                    delay *= backoff
            return wrapped_func(self, *args, **kwargs)

        return retry_wrapper

    return decorate
