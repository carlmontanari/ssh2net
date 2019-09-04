from difflib import Differ
from pathlib import Path
import re

import ssh2net


NET2_DIR = ssh2net.__file__
FUNC_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/tests/functional/iosxr/"

IOSXR_TEST = {"setup_host": "172.18.0.13", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}


def test_show_run_inputs():
    with ssh2net.SSH2Net(**IOSXR_TEST) as conn:
        show_run = conn.send_inputs("show run")[0][1].strip()
    with open(f"{FUNC_TEST_DIR}expected_output/show_run", "r") as f:
        expected_show_run = f.read().strip()

    # crypto strings on the vrnetlab devices change; replace w/ "CRYPTO" to parse
    show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", show_run)
    expected_show_run = re.sub(r"secret 5 \S*", "secret 5 CRYPTO", expected_show_run)

    d = Differ()
    diff = list(d.compare(show_run.splitlines()[1:], expected_show_run.splitlines()[1:]))
    diff = [line for line in diff if not line.startswith("  ")]
    if diff:
        print(diff)

    assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
    assert show_run.splitlines()[3:] == expected_show_run.splitlines()[3:]
