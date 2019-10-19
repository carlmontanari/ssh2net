import os
from pathlib import Path
import sys

import pytest

import ssh2net
from ssh2net import SSH2NetSSHConfig
from ssh2net.ssh_config import Host


NET2_DIR = ssh2net.__file__
UNIT_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/unit/"


def test_init_ssh_config_file_explicit():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    with open(f"{UNIT_TEST_DIR}_ssh_config", "r") as f:
        ssh_config_file = f.read()
    assert ssh_conf.ssh_config_file == ssh_config_file


@pytest.mark.skipif(sys.platform.startswith("win"), reason="not supporting ssh config on windows")
def test_init_ssh_config_file_user(fs):
    fs.add_real_file("/etc/ssh/ssh_config", target_path=f"{os.path.expanduser('~')}/.ssh/config")
    ssh_conf = SSH2NetSSHConfig()
    with open(f"{os.path.expanduser('~')}/.ssh/config", "r") as f:
        ssh_config_file = f.read()
    assert ssh_conf.ssh_config_file == ssh_config_file


@pytest.mark.skipif(sys.platform.startswith("win"), reason="not supporting ssh config on windows")
def test_init_ssh_config_file_system(fs):
    fs.add_real_file("/etc/ssh/ssh_config")
    ssh_conf = SSH2NetSSHConfig()
    with open("/etc/ssh/ssh_config", "r") as f:
        ssh_config_file = f.read()
    assert ssh_conf.ssh_config_file == ssh_config_file


def test_init_ssh_config_file_no_config_file(fs):
    ssh_conf = SSH2NetSSHConfig()
    assert ssh_conf.hosts is None


def test_init_ssh_config_file_no_hosts():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}__init__.py")
    assert ssh_conf.hosts is None


def test_str():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    assert str(ssh_conf) == "SSH2NetSSHConfig Object"


def test_repr():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    assert repr(ssh_conf) == (
        "SSH2NetSSHConfig {'hosts': {'1.2.3.4 someswitch1': HostEntry {'hosts': '1.2.3.4 "
        "someswitch1', 'hostname': 'someswitch1.bogus.com', 'port': '1234', 'user': 'carl', "
        "'address_family': None, 'bind_address': None, 'connect_timeout': None, "
        "'identities_only': 'yes', 'identity_file': '~/.ssh/mysshkey', 'keyboard_interactive': "
        "None, 'password_authentication': None, 'preferred_authentication': None}, '*': HostEntry "
        "{'hosts': '*', 'hostname': None, 'port': None, 'user': 'carl', 'address_family': None, "
        "'bind_address': None, 'connect_timeout': None, 'identities_only': None, 'identity_file': "
        "None, 'keyboard_interactive': None, 'password_authentication': None, "
        "'preferred_authentication': None}, 'someswitch?': HostEntry {'hosts': 'someswitch?', "
        "'hostname': 'someswitch1.bogus.com', 'port': '1234', 'user': 'carl', 'address_family': "
        "None, 'bind_address': None, 'connect_timeout': None, 'identities_only': 'yes', "
        "'identity_file': '~/.ssh/mysshkey', 'keyboard_interactive': None, "
        "'password_authentication': None, 'preferred_authentication': None}}}"
    )


def test_bool_true():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    assert bool(ssh_conf) is True


def test_bool_false():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}__init__.py")
    assert bool(ssh_conf) is False


def test_host__str():
    host = Host()
    assert str(host) == "Host: None"


def test_host__repr():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    assert repr(ssh_conf.hosts["1.2.3.4 someswitch1"]) == (
        "HostEntry {'hosts': '1.2.3.4 someswitch1', 'hostname': 'someswitch1.bogus.com', 'port': "
        "'1234', 'user': 'carl', 'address_family': None, 'bind_address': None, 'connect_timeout': "
        "None, 'identities_only': 'yes', 'identity_file': '~/.ssh/mysshkey', "
        "'keyboard_interactive': None, 'password_authentication': None, 'preferred_authentication': "
        "None}"
    )


def test_host_lookup_exact_host():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    host = ssh_conf.lookup("1.2.3.4 someswitch1")
    assert repr(host) == (
        "HostEntry {'hosts': '1.2.3.4 someswitch1', 'hostname': 'someswitch1.bogus.com', 'port': "
        "'1234', 'user': 'carl', 'address_family': None, 'bind_address': None, 'connect_timeout': "
        "None, 'identities_only': 'yes', 'identity_file': '~/.ssh/mysshkey', "
        "'keyboard_interactive': None, 'password_authentication': None, 'preferred_authentication':"
        " None}"
    )


def test_host_lookup_exact_host_in_list():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    host = ssh_conf.lookup("someswitch1")
    assert repr(host) == (
        "HostEntry {'hosts': '1.2.3.4 someswitch1', 'hostname': 'someswitch1.bogus.com', 'port': "
        "'1234', 'user': 'carl', 'address_family': None, 'bind_address': None, 'connect_timeout': "
        "None, 'identities_only': 'yes', 'identity_file': '~/.ssh/mysshkey', "
        "'keyboard_interactive': None, 'password_authentication': None, 'preferred_authentication':"
        " None}"
    )


def test_host_lookup_host_fuzzy():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    host = ssh_conf.lookup("someswitch2")
    assert repr(host) == (
        "HostEntry {'hosts': 'someswitch?', 'hostname': 'someswitch1.bogus.com', 'port': "
        "'1234', 'user': 'carl', 'address_family': None, 'bind_address': None, 'connect_timeout': "
        "None, 'identities_only': 'yes', 'identity_file': '~/.ssh/mysshkey', "
        "'keyboard_interactive': None, 'password_authentication': None, 'preferred_authentication': "
        "None}"
    )


def test_host_lookup_host_fuzzy_multi_match():
    ssh_conf = SSH2NetSSHConfig(f"{UNIT_TEST_DIR}_ssh_config")
    host = ssh_conf.lookup("someswitch9999")
    assert repr(host) == (
        "HostEntry {'hosts': 'someswitch?', 'hostname': 'someswitch1.bogus.com', 'port': "
        "'1234', 'user': 'carl', 'address_family': None, 'bind_address': None, 'connect_timeout': "
        "None, 'identities_only': 'yes', 'identity_file': '~/.ssh/mysshkey', "
        "'keyboard_interactive': None, 'password_authentication': None, 'preferred_authentication': "
        "None}"
    )
