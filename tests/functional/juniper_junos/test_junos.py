from pathlib import Path
import re

import pytest

from tests.functional.base_functional_tests import BaseFunctionalTest
import ssh2net

TEST_DEVICE = {
    "setup_host": "172.18.0.15",
    "auth_user": "vrnetlab",
    "auth_password": "VR-netlab9",
    "comms_disable_paging": "set cli screen-length 0",
}

dummy_conn = ssh2net.core.JunosDriver(**TEST_DEVICE)
PRIV_LEVELS = dummy_conn.privs


class TestJunos(BaseFunctionalTest):
    def setup_method(self):
        self.platform_driver = ssh2net.core.JunosDriver

        self.device_type = Path(__file__).resolve().parts[-2]
        self.func_test_dir = (
            f"{Path(ssh2net.__file__).parents[1]}/tests/functional/{self.device_type}/"
        )
        self.test_device = TEST_DEVICE
        self.disable_paging_ext_function = f"tests.functional.{self.device_type}.ext_test_funcs.{self.device_type.split('_')[1]}_disable_paging"

    @staticmethod
    def _replace_trailing_chars_running_config(input_data):
        execute_trailing_chars_pattern = re.compile(r"^}\s$", flags=re.M | re.I | re.S)
        input_data = re.sub(execute_trailing_chars_pattern, "}", input_data)
        return input_data

    @staticmethod
    def _replace_timestamps(input_data):
        datetime_pattern = re.compile(
            r"^## Last commit: \d+-\d+-\d+\s\d+:\d+:\d+\s\w+.*$", flags=re.M | re.I
        )
        input_data = re.sub(datetime_pattern, "TIME_STAMP_REPLACED", input_data)
        return input_data

    @staticmethod
    def _replace_crypto_strings(input_data):
        crypto_pattern = re.compile(
            r'^\s+encrypted-password\s"[\w$\.\/]+";\s.*$', flags=re.M | re.I
        )
        input_data = re.sub(crypto_pattern, "CRYPTO_REPLACED", input_data)
        return input_data

    def _disable_paging_function(self, setup_use_paramiko):
        test_device_copy = self.test_device.copy()
        test_device_copy.pop("comms_disable_paging")
        with ssh2net.SSH2Net(
            **test_device_copy,
            setup_use_paramiko=setup_use_paramiko,
            comms_disable_paging=self.disable_paging,
        ) as conn:
            show_run = conn.send_inputs("show configuration")[0]
        show_run = self.clean_input_data(show_run)
        return show_run

    def _disable_paging_external_function(self, setup_use_paramiko):
        test_device_copy = self.test_device.copy()
        test_device_copy.pop("comms_disable_paging")
        with ssh2net.SSH2Net(
            **test_device_copy,
            setup_use_paramiko=setup_use_paramiko,
            comms_disable_paging=self.disable_paging_ext_function,
        ) as conn:
            show_run = conn.send_inputs("show configuration")[0]
        show_run = self.clean_input_data(show_run)
        return show_run

    def disable_paging(self, cls):
        cls.send_inputs("set cli screen-length 0")

    def test_show_run_execute(self):
        pytest.skip("no support for execute on junos")

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_show_run_inputs(self, setup_use_paramiko):
        command = "show configuration"
        super().test_show_run_inputs(setup_use_paramiko, command)

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_show_run_inputs_no_strip_prompt(self, setup_use_paramiko):
        command = "show configuration"
        super().test_show_run_inputs_no_strip_prompt(setup_use_paramiko, command)

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_send_inputs_interact(self, setup_use_paramiko):
        interact = ["start shell user root", "Password:", TEST_DEVICE["auth_password"], r"^root@%$"]
        super().test_send_inputs_interact(setup_use_paramiko, interact, hidden_response=True)

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    @pytest.mark.parametrize("priv_level", [priv for priv in PRIV_LEVELS.values()])
    def test_acquire_all_priv_levels(self, setup_use_paramiko, priv_level):
        super().test_acquire_all_priv_levels(setup_use_paramiko, priv_level)
