from difflib import Differ
from pathlib import Path
import re

import ssh2net


def iosxr_pre_login_handler(cls):
    import time

    time.sleep(1)


PRE_LOGIN_HANDLER = iosxr_pre_login_handler


NET2_DIR = ssh2net.__file__
FUNC_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/functional/cisco_iosxr/"

IOSXR_TEST = {
    "setup_host": "172.18.0.13",
    "auth_user": "vrnetlab",
    "auth_password": "VR-netlab9",
    "comms_pre_login_handler": PRE_LOGIN_HANDLER,
}


def test_show_run_execute():
    conn = ssh2net.SSH2Net(**IOSXR_TEST)
    show_run = conn.open_and_execute("show run")[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", show_run)
    expected_show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", expected_show_run)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[4:] == expected_show_run.splitlines()[4:]


def test_show_run_inputs():
    with ssh2net.SSH2Net(**IOSXR_TEST) as conn:
        show_run = conn.send_inputs("show run")[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", show_run)
    expected_show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[4:], expected_show_run.splitlines()[4:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[4:] == expected_show_run.splitlines()[4:]


def test_show_run_inputs_no_strip():
    with ssh2net.SSH2Net(**IOSXR_TEST) as conn:
        show_run = conn.send_inputs("show run", strip_prompt=False)[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run_no_strip", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", show_run)
    expected_show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[4:], expected_show_run.splitlines()[4:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[4:] == expected_show_run.splitlines()[4:]


def test_send_inputs_interact():
    with ssh2net.SSH2Net(**IOSXR_TEST) as conn:
        current_prompt = conn.get_prompt()
        interactive = conn.send_inputs_interact(
            ("clear logg", "Clear logging buffer [confirm] [y/n] :", "y", current_prompt)
        )[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/interactive", "r") as f:
        expected_interactive = f.read().strip()

    d = Differ()
    diff = list(d.compare(interactive.splitlines(), expected_interactive.splitlines()))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(interactive.splitlines()) == len(expected_interactive.splitlines())
    # cisco_iosxr prints date/time before this prompt; strip that so things match
    assert interactive.splitlines()[1:] == expected_interactive.splitlines()[1:]


def test_disable_paging_function():
    def disable_paging_func(cls):
        cls.send_inputs("term length 0")

    disable_paging = disable_paging_func
    with ssh2net.SSH2Net(**IOSXR_TEST, comms_disable_paging=disable_paging) as conn:
        show_run = conn.send_inputs("show run")[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", show_run)
    expected_show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[4:], expected_show_run.splitlines()[4:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[4:] == expected_show_run.splitlines()[4:]


def test_disable_paging_external_function():
    with ssh2net.SSH2Net(
        **IOSXR_TEST,
        comms_disable_paging="tests.functional.cisco_iosxr.ext_test_funcs.iosxr_disable_paging",
    ) as conn:
        show_run = conn.send_inputs("show run")[0][1]
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", show_run)
    expected_show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[4:], expected_show_run.splitlines()[4:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[4:] == expected_show_run.splitlines()[4:]
