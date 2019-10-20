from pathlib import Path
import pytest
import sys

import ssh2net
from ssh2net import SSH2Net
from ssh2net.exceptions import ValidationError, SetupTimeout


NET2_DIR = ssh2net.__file__
UNIT_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/unit/"


def test_init__shell():
    test_host = {"setup_host": "my_device  ", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert conn._shell is False


def test_init_host_strip():
    test_host = {"setup_host": "my_device  ", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert conn.host == "my_device"


def test_init_validate_host():
    test_host = {
        "setup_host": "8.8.8.8",
        "setup_validate_host": True,
        "auth_user": "username",
        "auth_password": "password",
    }
    conn = SSH2Net(**test_host)
    assert conn.host == "8.8.8.8"


def test_init_valid_port():
    test_host = {
        "setup_host": "my_device  ",
        "setup_port": 123,
        "auth_user": "username",
        "auth_password": "password",
    }
    conn = SSH2Net(**test_host)
    assert conn.port == 123


def test_init_invalid_port():
    test_host = {
        "setup_host": "my_device  ",
        "setup_port": "notanint",
        "auth_user": "username",
        "auth_password": "password",
    }
    with pytest.raises(ValueError):
        SSH2Net(**test_host)


def test_init_valid_setup_timeout():
    test_host = {
        "setup_host": "my_device  ",
        "setup_timeout": 10,
        "auth_user": "username",
        "auth_password": "password",
    }
    conn = SSH2Net(**test_host)
    assert conn.setup_timeout == 10


def test_init_invalid_setup_timeout():
    test_host = {
        "setup_host": "my_device  ",
        "setup_timeout": "notanint",
        "auth_user": "username",
        "auth_password": "password",
    }
    with pytest.raises(ValueError):
        SSH2Net(**test_host)


def test_init_valid_session_timeout():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_timeout": 10,
    }
    conn = SSH2Net(**test_host)
    assert conn.session_timeout == 10


def test_init_invalid_session_timeout():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_timeout": "notanint",
    }
    with pytest.raises(ValueError):
        SSH2Net(**test_host)


def test_init_valid_session_keepalive():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_keepalive": True,
    }
    conn = SSH2Net(**test_host)
    assert conn.session_keepalive is True


def test_init_invalid_session_keepalive():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_keepalive": "notabool",
    }
    with pytest.raises(ValueError):
        SSH2Net(**test_host)


def test_init_valid_session_keepalive_interval():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_keepalive_interval": 10,
    }
    conn = SSH2Net(**test_host)
    assert conn.session_keepalive_interval == 10


def test_init_invalid_session_keepalive_interval():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_keepalive_interval": "notanint",
    }
    with pytest.raises(ValueError):
        SSH2Net(**test_host)


def test_init_valid_session_keepalive_type():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_keepalive_type": "standard",
    }
    conn = SSH2Net(**test_host)
    assert conn.session_keepalive_type == "standard"


def test_init_invalid_session_keepalive_type():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_keepalive_type": "notvalid",
    }
    with pytest.raises(ValueError):
        SSH2Net(**test_host)


def test_init_valid_session_keepalive_pattern():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "session_keepalive_pattern": "\007",
    }
    conn = SSH2Net(**test_host)
    assert conn.session_keepalive_pattern == "\x07"


def test_init_username_strip():
    test_host = {"setup_host": "my_device", "auth_user": "username  ", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert conn.auth_user == "username"


def test_init_password_strip():
    test_host = {"setup_host": "my_device", "auth_user": "username", "auth_password": "password  "}
    conn = SSH2Net(**test_host)
    assert conn.auth_password == "password"


def test_init_ssh_key_strip():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_public_key": "/some/public/key  ",
    }
    conn = SSH2Net(**test_host)
    assert conn.auth_public_key == b"/some/public/key"


def test_init_valid_comms_prompt_regex():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_prompt_regex": "somestr",
    }
    conn = SSH2Net(**test_host)
    assert conn.comms_prompt_regex == "somestr"


def test_init_invalid_comms_prompt_regex():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_prompt_regex": 123,
    }
    with pytest.raises(TypeError):
        SSH2Net(**test_host)


def test_init_valid_comms_prompt_timeout():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "comms_operation_timeout": 10,
    }
    conn = SSH2Net(**test_host)
    assert conn.comms_operation_timeout == 10


def test_init_invalid_comms_prompt_timeout():
    test_host = {
        "setup_host": "my_device  ",
        "auth_user": "username",
        "auth_password": "password",
        "comms_operation_timeout": "notanint",
    }
    with pytest.raises(ValueError):
        SSH2Net(**test_host)


def test_init_valid_comms_return_char():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_return_char": "\rn",
    }
    conn = SSH2Net(**test_host)
    assert conn.comms_return_char == "\rn"


def test_init_invalid_comms_return_char():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_return_char": False,
    }
    with pytest.raises(ValueError) as e:
        SSH2Net(**test_host)
    assert str(e.value) == "'comms_return_char' must be <class 'str'>, got: <class 'bool'>'"


def test_init_valid_comms_pre_login_handler_func():
    def pre_login_handler_func():
        pass

    login_handler = pre_login_handler_func
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_pre_login_handler": login_handler,
    }
    conn = SSH2Net(**test_host)
    assert callable(conn.comms_pre_login_handler)


def test_init_valid_comms_pre_login_handler_ext_func():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_pre_login_handler": "tests.unit.ext_test_funcs.some_pre_login_handler_func",
    }
    conn = SSH2Net(**test_host)
    assert callable(conn.comms_pre_login_handler)


def test_init_invalid_comms_pre_login_handler():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_pre_login_handler": "not.a.valid.ext.function",
    }
    with pytest.raises(ValueError) as e:
        SSH2Net(**test_host)
    assert (
        str(e.value)
        == f"{test_host['comms_pre_login_handler']} is an invalid comms_pre_login_handler function or path to a function."
    )


def test_init_valid_comms_disable_paging_default():
    test_host = {"setup_host": "my_device", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert conn.comms_disable_paging == "term length 0"


def test_init_valid_comms_disable_paging_func():
    def disable_paging_func():
        pass

    disable_paging = disable_paging_func
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_disable_paging": disable_paging,
    }
    conn = SSH2Net(**test_host)
    assert callable(conn.comms_disable_paging)


def test_init_valid_comms_disable_paging_ext_func():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_disable_paging": "tests.unit.ext_test_funcs.some_disable_paging_func",
    }
    conn = SSH2Net(**test_host)
    assert callable(conn.comms_disable_paging)


def test_init_valid_comms_disable_paging_str():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_disable_paging": "do some paging stuff",
    }
    conn = SSH2Net(**test_host)
    assert conn.comms_disable_paging == "do some paging stuff"


def test_init_invalid_comms_disable_paging_ext_func():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_disable_paging": "tests.unit.ext_test_funcs.some_disable_paging_func_BAD",
    }
    with pytest.raises(AttributeError):
        SSH2Net(**test_host)


def test_init_valid_comms_disable_paging_default():
    test_host = {"setup_host": "my_device", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert conn.comms_disable_paging == "terminal length 0"


def test_init_invalid_comms_disable_paging_str():
    test_host = {
        "setup_host": "my_device",
        "auth_user": "username",
        "auth_password": "password",
        "comms_disable_paging": 1234,
    }
    with pytest.raises(ValueError) as e:
        SSH2Net(**test_host)
    assert (
        str(e.value)
        == f"{test_host['comms_disable_paging']} is an invalid comms_disable_paging function, path to a function, or is not a string."
    )


def test_init_ssh_config_file():
    test_host = {
        "setup_host": "someswitch1",
        "setup_ssh_config_file": f"{UNIT_TEST_DIR}_ssh_config",
    }
    conn = SSH2Net(**test_host)
    assert conn.auth_user == "carl"


# will fail without mocking or a real host
# def test_enter_exit():
#    test_host = {"setup_host": "1.2.3.4", "auth_user": "username", "auth_password": "password"}
#    with SSH2Net(**test_host) as conn:
#        assert bool(conn) is True
#    assert bool(conn) is False


def test_str():
    test_host = {"setup_host": "1.2.3.4", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert str(conn) == f"SSH2Net Connection Object for host {test_host['setup_host']}"


def test_repr():
    test_host = {"setup_host": "1.2.3.4", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert repr(conn) == (
        f"SSH2Net {{'_shell': False, 'host': '{test_host['setup_host']}', 'port': 22, "
        "'setup_timeout': 5, 'setup_use_paramiko': False, 'session_timeout': 5000, "
        "'session_keepalive': False, 'session_keepalive_interval': 10, 'session_keepalive_type': "
        fr"'network', 'session_keepalive_pattern': '\x05', 'auth_user': '{test_host['auth_user']}',"
        " 'auth_public_key': None, 'auth_password': '********', 'comms_prompt_regex': "
        r"'^[a-z0-9.\\-@()/:]{1,32}[#>$]$', 'comms_operation_timeout': 10, "
        r"'comms_return_char': '\n', 'comms_pre_login_handler': '', 'comms_disable_paging': "
        "'terminal length 0'}"
    )


def test_bool():
    test_host = {"setup_host": "my_device  ", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert bool(conn) is False


def test__validate_host_valid_ip():
    test_host = {"setup_host": "8.8.8.8", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    r = conn._validate_host()
    assert r is None


def test__validate_host_valid_dns():
    test_host = {"setup_host": "google.com", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    r = conn._validate_host()
    assert r is None


def test__validate_host_invalid_ip():
    test_host = {
        "setup_host": "255.255.255.256",
        "auth_user": "username",
        "auth_password": "password",
    }
    conn = SSH2Net(**test_host)
    with pytest.raises(ValidationError) as e:
        conn._validate_host()
    assert str(e.value) == f"Host {test_host['setup_host']} is not an IP or resolvable DNS name."


def test__validate_host_invalid_dns():
    test_host = {
        "setup_host": "notresolvablename",
        "auth_user": "username",
        "auth_password": "password",
    }
    conn = SSH2Net(**test_host)
    with pytest.raises(ValidationError) as e:
        conn._validate_host()
    assert str(e.value) == f"Host {test_host['setup_host']} is not an IP or resolvable DNS name."


def test__socket_alive_false():
    test_host = {"setup_host": "127.0.0.1", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    assert conn._socket_alive() is False


@pytest.mark.skipif(sys.platform.startswith("win"), reason="no ssh server for windows")
def test__socket_alive_true():
    test_host = {"setup_host": "127.0.0.1", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
    conn._socket_open()
    assert conn._socket_alive() is True


@pytest.mark.skipif(sys.platform.startswith("win"), reason="no ssh server for windows")
def test__socket_close():
    test_host = {"setup_host": "127.0.0.1", "auth_user": "username", "auth_password": "password"}
    conn = SSH2Net(**test_host)
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
    conn = SSH2Net(**test_host)
    with pytest.raises(SetupTimeout):
        conn._socket_open()
