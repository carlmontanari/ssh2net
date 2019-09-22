from difflib import Differ
from pathlib import Path
import re

import ssh2net


NET2_DIR = ssh2net.__file__
FUNC_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/functional/juniper_junos/"

JUNOS_TEST = {"setup_host": "172.18.0.15", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}


def test_show_run_inputs():
    with ssh2net.SSH2Net(**JUNOS_TEST, comms_disable_paging="set cli screen-length 0") as conn:
        show_configuration = conn.send_inputs("show configuration")[0].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_configuration", "r") as f:
        expected_show_configuration = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", show_configuration
    )
    expected_show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", expected_show_configuration
    )

    d = Differ()
    diff = list(
        d.compare(show_configuration.splitlines()[1:], expected_show_configuration.splitlines()[1:])
    )
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_configuration.splitlines()) == len(expected_show_configuration.splitlines())
    assert show_configuration.splitlines()[1:] == expected_show_configuration.splitlines()[1:]


def test_show_run_inputs_no_strip_prompt():
    with ssh2net.SSH2Net(**JUNOS_TEST, comms_disable_paging="set cli screen-length 0") as conn:
        show_configuration = conn.send_inputs("show configuration", strip_prompt=False)[0].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_configuration_no_strip", "r") as f:
        expected_show_configuration = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", show_configuration
    )
    expected_show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", expected_show_configuration
    )

    d = Differ()
    diff = list(
        d.compare(show_configuration.splitlines()[4:], expected_show_configuration.splitlines()[4:])
    )
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_configuration.splitlines()) == len(expected_show_configuration.splitlines())
    assert show_configuration.splitlines()[1:] == expected_show_configuration.splitlines()[1:]


def test_send_inputs_interact():
    with ssh2net.SSH2Net(**JUNOS_TEST, comms_disable_paging="set cli screen-length 0") as conn:
        interactive = conn.send_inputs_interact(
            ("start shell user root", "Password:", JUNOS_TEST["auth_password"], r"^root@%$"),
            hidden_response=True,
        )[0]
    with open(f"{FUNC_TEST_DIR}expected_output/interactive", "r") as f:
        expected_interactive = f.read().strip()

    d = Differ()
    diff = list(d.compare(interactive.splitlines(), expected_interactive.splitlines()))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(interactive.splitlines()) == len(expected_interactive.splitlines())
    assert interactive.splitlines() == expected_interactive.splitlines()


def test_disable_paging_function():
    def disable_paging_func(cls):
        cls.send_inputs("set cli screen-length 0")

    disable_paging = disable_paging_func
    with ssh2net.SSH2Net(**JUNOS_TEST, comms_disable_paging=disable_paging) as conn:
        show_configuration = conn.send_inputs("show configuration")[0].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_configuration", "r") as f:
        expected_show_configuration = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", show_configuration
    )
    expected_show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", expected_show_configuration
    )

    d = Differ()
    diff = list(
        d.compare(show_configuration.splitlines()[1:], expected_show_configuration.splitlines()[1:])
    )
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_configuration.splitlines()) == len(expected_show_configuration.splitlines())
    assert show_configuration.splitlines()[1:] == expected_show_configuration.splitlines()[1:]


def test_disable_paging_external_function():
    with ssh2net.SSH2Net(
        **JUNOS_TEST,
        comms_disable_paging="tests.functional.juniper_junos.ext_test_funcs.junos_disable_paging",
    ) as conn:
        show_configuration = conn.send_inputs("show configuration")[0].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_configuration", "r") as f:
        expected_show_configuration = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", show_configuration
    )
    expected_show_configuration = re.sub(
        r"encrypted-password \S*", "encrypted-password CRYPTO", expected_show_configuration
    )

    d = Differ()
    diff = list(
        d.compare(show_configuration.splitlines()[1:], expected_show_configuration.splitlines()[1:])
    )
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_configuration.splitlines()) == len(expected_show_configuration.splitlines())
    assert show_configuration.splitlines()[1:] == expected_show_configuration.splitlines()[1:]
