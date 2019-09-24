from io import TextIOWrapper
import pkg_resources

from ssh2net.helper import transform_netmiko_kwargs, _textfsm_get_template, textfsm_parse


IOS_ARP = """Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  172.31.254.1            -   0000.0c07.acfe  ARPA   Vlan254
Internet  172.31.254.2            -   c800.84b2.e9c2  ARPA   Vlan254
"""


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
    assert transformed_args["comms_prompt_timeout"] == 50


def test_transform_netmiko_args_setup_timeout():
    netmiko_args = {"host": "1.2.3.4", "username": "person", "password": "password", "port": 123}
    transformed_args = transform_netmiko_kwargs(netmiko_args)
    assert transformed_args["setup_host"] == "1.2.3.4"
    assert transformed_args["comms_prompt_timeout"] == 5


def test__textfsm_get_template_valid_template():
    template = _textfsm_get_template("cisco_nxos", "show ip arp")
    template_dir = pkg_resources.resource_filename("ntc_templates", "templates")
    assert isinstance(template, TextIOWrapper)
    assert template.name == f"{template_dir}/cisco_nxos_show_ip_arp.template"


def test__textfsm_get_template_invalid_template():
    template = _textfsm_get_template("cisco_nxos", "show racecar")
    assert not template


def test_text_textfsm_parse_success():
    template = _textfsm_get_template("cisco_ios", "show ip arp")
    result = textfsm_parse(template, IOS_ARP)
    assert isinstance(result, list)
    assert result[0] == ["Internet", "172.31.254.1", "-", "0000.0c07.acfe", "ARPA", "Vlan254"]


def test_text_textfsm_parse_success_string_path():
    template = _textfsm_get_template("cisco_ios", "show ip arp")
    result = textfsm_parse(template.name, IOS_ARP)
    assert isinstance(result, list)
    assert result[0] == ["Internet", "172.31.254.1", "-", "0000.0c07.acfe", "ARPA", "Vlan254"]


def test_text_textfsm_parse_failure():
    template = _textfsm_get_template("cisco_ios", "show ip arp")
    result = textfsm_parse(template, "not really arp data")
    assert isinstance(result, str)
    assert result == "not really arp data"
