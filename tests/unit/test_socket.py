import sys
from pathlib import Path

import pytest

import ssh2net
from ssh2net import SSH2NetBase
from ssh2net.exceptions import SetupTimeout

NET2_DIR = ssh2net.__file__
UNIT_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/unit/"


def test__socket_alive_false():
    test_host = {"setup_host": "127.0.0.1", "auth_user": "username", "auth_password": "password"}
    conn = SSH2NetBase(**test_host)
    assert conn._socket_alive() is False


@pytest.mark.skipif(sys.platform.startswith("win"), reason="no ssh server for windows")
def test__socket_alive_true():
    test_host = {"setup_host": "127.0.0.1", "auth_user": "username", "auth_password": "password"}
    conn = SSH2NetBase(**test_host)
    conn._socket_open()
    assert conn._socket_alive() is True


@pytest.mark.skipif(sys.platform.startswith("win"), reason="no ssh server for windows")
def test__socket_close():
    test_host = {"setup_host": "127.0.0.1", "auth_user": "username", "auth_password": "password"}
    conn = SSH2NetBase(**test_host)
    conn._socket_open()
    assert conn._socket_alive() is True
    conn._socket_close()
    assert conn._socket_alive() is False


@pytest.mark.skipif(sys.platform.startswith("win"), reason="no ssh server for windows")
def test__socket_open_timeout():
    test_host = {
        "setup_host": "240.0.0.1",
        "setup_timeout": 1,
        "auth_user": "username",
        "auth_password": "password",
    }
    conn = SSH2NetBase(**test_host)
    with pytest.raises(SetupTimeout):
        conn._socket_open()
