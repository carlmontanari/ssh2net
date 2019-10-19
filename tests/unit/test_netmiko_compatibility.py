import pytest

from ssh2net.netmiko_compatibility import connect_handler, transform_netmiko_kwargs


def test_connect_handler_invalid_device_type():
    device = {"device_type": "tacocat"}
    with pytest.raises(TypeError):
        connect_handler(**device)


def test_connect_handler_ip_no_hostname():
    netmiko_args = {
        "ip": "1.2.3.4",
        "username": "person",
        "password": "password",
        "port": 123,
        "global_delay_factor": 5,
        "device_type": "cisco_xe",
    }
    conn = connect_handler(auto_open=False, **netmiko_args)
    assert conn.textfsm_platform == "cisco_ios"


def test_connect_handler_valid_connection():
    netmiko_args = {
        "host": "1.2.3.4",
        "username": "person",
        "password": "password",
        "port": 123,
        "global_delay_factor": 5,
        "device_type": "cisco_xe",
    }
    conn = connect_handler(auto_open=False, **netmiko_args)
    assert conn.textfsm_platform == "cisco_ios"


def test_transform_netmiko_args():
    netmiko_args = {
        "host": "1.2.3.4",
        "username": "person",
        "password": "password",
        "port": 123,
        "global_delay_factor": 5,
    }
    transformed_args = transform_netmiko_kwargs(netmiko_args)
    assert transformed_args["setup_host"] == "1.2.3.4"
    assert transformed_args["session_timeout"] == 25000


def test_transform_netmiko_args_setup_timeout():
    netmiko_args = {"host": "1.2.3.4", "username": "person", "password": "password", "port": 123}
    transformed_args = transform_netmiko_kwargs(netmiko_args)
    assert transformed_args["setup_host"] == "1.2.3.4"
    assert transformed_args["session_timeout"] == 5000
