from difflib import Differ
from pathlib import Path
import re

import ssh2net


NET2_DIR = ssh2net.__file__
FUNC_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/functional/cisco_iosxe/"

IOSXE_TEST = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}


def test_show_run_execute():
    conn = ssh2net.SSH2Net(**IOSXE_TEST)
    show_run = conn.open_and_execute("show run")[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run_execute", "r") as f:
        expected_show_run = f.read()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", show_run).replace(
        "\t", "  "
    )
    expected_show_run = re.sub(
        r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", expected_show_run
    )

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]


def test_show_run_inputs():
    with ssh2net.SSH2Net(**IOSXE_TEST) as conn:
        show_run = conn.send_inputs("show run")[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", show_run)
    expected_show_run = re.sub(
        r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", expected_show_run
    )

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[7:], expected_show_run.splitlines()[7:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]


def test_show_run_inputs_no_strip_prompt():
    with ssh2net.SSH2Net(**IOSXE_TEST) as conn:
        show_run = conn.send_inputs("show run", strip_prompt=False)[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run_no_strip", "r") as f:
        expected_show_run = f.read().strip()  # strip off extra space after prompt to match ssh2net

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", show_run)
    expected_show_run = re.sub(
        r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", expected_show_run
    )

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[7:], expected_show_run.splitlines()[7:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]


def test_send_inputs_interact():
    with ssh2net.SSH2Net(**IOSXE_TEST) as conn:
        current_prompt = conn.get_prompt()
        interactive = conn.send_inputs_interact(
            ("clear logg", "Clear logging buffer [confirm]", "", current_prompt)
        )[0][1]
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
        cls.send_inputs("term length 0")

    disable_paging = disable_paging_func
    with ssh2net.SSH2Net(**IOSXE_TEST, comms_disable_paging=disable_paging) as conn:
        show_run = conn.send_inputs("show run")[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", show_run)
    expected_show_run = re.sub(
        r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", expected_show_run
    )

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[7:], expected_show_run.splitlines()[7:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]


def test_disable_paging_external_function():
    with ssh2net.SSH2Net(
        **IOSXE_TEST,
        comms_disable_paging="tests.functional.cisco_iosxe.ext_test_funcs.iosxe_disable_paging",
    ) as conn:
        show_run = conn.send_inputs("show run")[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", show_run)
    expected_show_run = re.sub(
        r" certificate self-signed 01(\n\s(\s\w+)*)*", "CRYPTO", expected_show_run
    )

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[7:], expected_show_run.splitlines()[7:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]
