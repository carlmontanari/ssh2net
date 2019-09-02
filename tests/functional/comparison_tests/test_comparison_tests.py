from pathlib import Path
import subprocess

import ssh2net


NET2_DIR = ssh2net.__file__
COMPARISON_TEST_DIR = f"{Path(NET2_DIR).parents[1]}/comparison_tests/"


def subprocess_runner(cmd, cwd):
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd) as proc:
        std_out, std_err = proc.communicate()
    return (std_out.decode(), std_err.decode(), proc.returncode)


def test_test_net2():
    cmd = ["python", "test_net2.py"]
    std_out, std_err, return_code = subprocess_runner(cmd, COMPARISON_TEST_DIR)
    assert return_code == 0
    assert std_err == ""


def test_test_netmiko():
    cmd = ["python", "test_netmiko.py"]
    std_out, std_err, return_code = subprocess_runner(cmd, COMPARISON_TEST_DIR)
    assert return_code == 0
    assert std_err == ""
