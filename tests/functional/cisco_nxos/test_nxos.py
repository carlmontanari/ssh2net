from difflib import Differ
from pathlib import Path
import re

import ssh2net


NET2_DIR = ssh2net.__file__
FUNC_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/functional/cisco_nxos/"

NXOS_TEST = {"setup_host": "172.18.0.12", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}


def test_show_run_execute():
    conn = ssh2net.SSH2Net(**NXOS_TEST)
    show_run = conn.open_and_execute("show run")[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", show_run)
    expected_show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", expected_show_run)
    show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", show_run)
    expected_show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", expected_show_run)
    show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", show_run)
    expected_show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", expected_show_run)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]


def test_show_run_inputs():
    conn = ssh2net.SSH2Net(**NXOS_TEST)
    conn.open_shell()
    show_run = conn.send_inputs("show run")[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", show_run)
    expected_show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", expected_show_run)
    show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", show_run)
    expected_show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", expected_show_run)
    show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", show_run)
    expected_show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[4:], expected_show_run.splitlines()[4:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[4:] == expected_show_run.splitlines()[4:]


def test_show_run_inputs_no_strip_prompt():
    conn = ssh2net.SSH2Net(**NXOS_TEST)
    conn.open_shell()
    show_run = conn.send_inputs("show run", strip_prompt=False)[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run_no_strip", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", show_run)
    expected_show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", expected_show_run)
    show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", show_run)
    expected_show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", expected_show_run)
    show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", show_run)
    expected_show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[4:], expected_show_run.splitlines()[4:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[4:] == expected_show_run.splitlines()[4:]


def test_send_inputs_interact():
    """
    expected output for this test is somewhat massaged to make this test pass
    in "real" device ssh session there aren't new lines between response and the prompt
    there is also a space after the prompt and before the "n"
    i think given that this is just for interactive "solving" these problems is not worht it
    """
    with ssh2net.SSH2Net(**NXOS_TEST) as conn:
        current_prompt = conn.get_prompt()
        interactive = conn.send_inputs_interact(
            ("delete bootflash:virtual-instance.conf", "(yes/no/abort)   [y]", "n", current_prompt)
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
    with ssh2net.SSH2Net(**NXOS_TEST, comms_disable_paging=disable_paging) as conn:
        show_run = conn.send_inputs("show run")[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", show_run)
    expected_show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", expected_show_run)
    show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", show_run)
    expected_show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", expected_show_run)
    show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", show_run)
    expected_show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[7:], expected_show_run.splitlines()[7:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]


def test_disable_paging_external_function():
    with ssh2net.SSH2Net(
        **NXOS_TEST,
        comms_disable_paging="tests.functional.cisco_nxos.ext_test_funcs.nxos_disable_paging",
    ) as conn:
        show_run = conn.send_inputs("show run")[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", show_run)
    expected_show_run = re.sub(r"password 5 \S*", "password 5  CRYPTO", expected_show_run)
    show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", show_run)
    expected_show_run = re.sub(r"auth md5 \S*", "auth md5  CRYPTO", expected_show_run)
    show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", show_run)
    expected_show_run = re.sub(r"CRYPTO priv \S*", "CRYPTO priv CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[7:], expected_show_run.splitlines()[7:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[7:] == expected_show_run.splitlines()[7:]
