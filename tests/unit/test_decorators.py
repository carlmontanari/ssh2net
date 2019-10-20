import sys
import time

import pytest

from ssh2net import SSH2Net

if not sys.platform.startswith("win"):
    from ssh2net.decorators import operation_timeout
else:
    from ssh2net.decorators import operation_timeout_win as operation_timeout


class MockSSH2Net(SSH2Net):
    def __init__(self):
        super().__init__()
        self.comms_operation_timeout = 0.1

    @operation_timeout("comms_operation_timeout")
    def operation_timeout_func(self):
        time.sleep(1000)

    @operation_timeout("comms_operation_timeout")
    def operation_success_func(self):
        time.sleep(0.00001)


def test_operation_timeout_timeout():
    timeout_test = MockSSH2Net()
    with pytest.raises(TimeoutError):
        timeout_test.operation_timeout_func()


def test_operation_timeout_success():
    timeout_test = MockSSH2Net()
    timeout_test.operation_success_func()


def test_operation_timeout_no_timeout_value():
    timeout_test = MockSSH2Net()
    timeout_test.comms_prompt_timeout = None
    timeout_test.operation_success_func()
