import re
from pathlib import Path

import pytest

import ssh2net
from tests.functional.base_functional_tests import BaseFunctionalTest, paramiko_present

TEST_DEVICE = {"setup_host": "172.18.0.14", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}

dummy_conn = ssh2net.core.IOSXEDriver(**TEST_DEVICE)
PRIV_LEVELS = dummy_conn.privs


class TestEOS(BaseFunctionalTest):
    def setup_method(self):
        self.platform_driver = ssh2net.core.EOSDriver

        self.device_type = Path(__file__).resolve().parts[-2]
        self.func_test_dir = (
            f"{Path(ssh2net.__file__).parents[1]}/tests/functional/{self.device_type}/"
        )
        self.test_device = TEST_DEVICE
        # ensure eos device gets into "priv_exec" mode since base image drops you into just "exec"
        self.test_device["comms_pre_login_handler"] = self.pre_login_handler
        self.disable_paging_ext_function = f"tests.functional.{self.device_type}.ext_test_funcs.{self.device_type.split('_')[1]}_disable_paging"

    @staticmethod
    def _replace_trailing_chars_running_config(input_data):
        execute_trailing_chars_pattern = re.compile(r"^end.*$", flags=re.M | re.I | re.S)
        input_data = re.sub(execute_trailing_chars_pattern, "end", input_data)
        return input_data

    @staticmethod
    def replace_timestamps(input_data):
        datetime_pattern = re.compile(
            r"(mon|tue|wed|thu|fri|sat|sun)\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d+\s+\d+:\d+:\d+\s+\d+$",
            flags=re.M | re.I,
        )
        input_data = re.sub(datetime_pattern, "TIME_STAMP_REPLACED", input_data)
        return input_data

    @staticmethod
    def _replace_crypto_strings(input_data):
        crypto_pattern = re.compile(r"secret\ssha512\s[\w$\.\/]+$", flags=re.M | re.I)
        input_data = re.sub(crypto_pattern, "CRYPTO_REPLACED", input_data)
        return input_data

    def disable_paging(self, cls):
        cls.send_inputs("term length 0")

    def pre_login_handler(self, cls):
        cls.send_inputs("enable")

    def test_show_run_execute(self):
        pytest.skip("no ssh2 support for keyboard interactive auth")

    @pytest.mark.parametrize(
        "setup_use_paramiko",
        [
            pytest.param(
                True,
                marks=pytest.mark.skipif(paramiko_present is False, reason="paramiko not present"),
            ),
        ],
        ids=["paramiko"],
    )
    def test_show_run_inputs(self, setup_use_paramiko):
        super().test_show_run_inputs(setup_use_paramiko)

    @pytest.mark.parametrize(
        "setup_use_paramiko",
        [
            pytest.param(
                True,
                marks=pytest.mark.skipif(paramiko_present is False, reason="paramiko not present"),
            ),
        ],
        ids=["paramiko"],
    )
    def test_show_run_inputs_no_strip_prompt(self, setup_use_paramiko):
        super().test_show_run_inputs_no_strip_prompt(setup_use_paramiko)

    @pytest.mark.parametrize(
        "setup_use_paramiko",
        [
            pytest.param(
                True,
                marks=pytest.mark.skipif(paramiko_present is False, reason="paramiko not present"),
            ),
        ],
        ids=["paramiko"],
    )
    def test_send_inputs_interact(self, setup_use_paramiko):
        pytest.skip("dont know what to do that is interactive on eos...?")

    @pytest.mark.parametrize(
        "setup_use_paramiko",
        [
            pytest.param(
                True,
                marks=pytest.mark.skipif(paramiko_present is False, reason="paramiko not present"),
            ),
        ],
        ids=["paramiko"],
    )
    def test_disable_paging_function(self, setup_use_paramiko):
        super().test_disable_paging_function(setup_use_paramiko)

    @pytest.mark.parametrize(
        "setup_use_paramiko",
        [
            pytest.param(
                True,
                marks=pytest.mark.skipif(paramiko_present is False, reason="paramiko not present"),
            ),
        ],
        ids=["paramiko"],
    )
    def test_disable_paging_external_function(self, setup_use_paramiko):
        super().test_disable_paging_external_function(setup_use_paramiko)

    @pytest.mark.parametrize(
        "setup_use_paramiko",
        [
            pytest.param(
                True,
                marks=pytest.mark.skipif(paramiko_present is False, reason="paramiko not present"),
            ),
        ],
        ids=["paramiko"],
    )
    @pytest.mark.parametrize("priv_level", [priv for priv in PRIV_LEVELS.values()])
    def test_acquire_all_priv_levels(self, setup_use_paramiko, priv_level):
        super().test_acquire_all_priv_levels(setup_use_paramiko, priv_level)

    @pytest.mark.parametrize(
        "setup_use_paramiko",
        [
            pytest.param(
                True,
                marks=pytest.mark.skipif(paramiko_present is False, reason="paramiko not present"),
            ),
        ],
        ids=["paramiko"],
    )
    def test__determine_current_priv_special_configuration(self, setup_use_paramiko):
        with self.platform_driver(
            **self.test_device, setup_use_paramiko=setup_use_paramiko
        ) as conn:
            conn.send_inputs(["configure terminal", "interface Ethernet1"])
            current_prompt = conn.get_prompt()
            current_priv = conn._determine_current_priv(current_prompt)
        assert current_priv.name == "special_configuration"
