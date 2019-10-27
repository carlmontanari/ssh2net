from pathlib import Path
import re

import pytest

from tests.functional.base_functional_tests import BaseFunctionalTest
import ssh2net

TEST_DEVICE = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}

dummy_conn = ssh2net.IOSXEDriver(**TEST_DEVICE)
PRIV_LEVELS = dummy_conn.privs


class TestIOSXE(BaseFunctionalTest):
    def setup_method(self):
        self.platform_driver = ssh2net.IOSXEDriver

        self.device_type = Path(__file__).resolve().parts[-2]
        self.func_test_dir = (
            f"{Path(ssh2net.__file__).parents[1]}/tests/functional/{self.device_type}/"
        )
        self.test_device = TEST_DEVICE
        self.disable_paging_ext_function = f"tests.functional.{self.device_type}.ext_test_funcs.{self.device_type.split('_')[1]}_disable_paging"

    @staticmethod
    def _replace_trailing_chars_running_config(input_data):
        execute_trailing_chars_pattern = re.compile(r"^end.*$", flags=re.M | re.I | re.S)
        input_data = re.sub(execute_trailing_chars_pattern, "end", input_data)
        return input_data

    @staticmethod
    def _replace_config_bytes(input_data):
        config_bytes_pattern = re.compile(r"^Current configuration : \d+ bytes$", flags=re.M | re.I)
        input_data = re.sub(
            config_bytes_pattern, "Current configuration : CONFIG_BYTES", input_data
        )
        return input_data

    @staticmethod
    def _replace_timestamps(input_data):
        datetime_pattern = re.compile(
            r"\d+:\d+:\d+\d+\s+[a-z]{3}\s+(mon|tue|wed|thu|fri|sat|sun)\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d+\s+\d+",
            flags=re.M | re.I,
        )
        input_data = re.sub(datetime_pattern, "TIME_STAMP_REPLACED", input_data)
        return input_data

    @staticmethod
    def _replace_configured_by(input_data):
        configured_by_pattern = re.compile(
            r"^! Last configuration change at TIME_STAMP_REPLACED by (\w+)$", flags=re.M | re.I
        )
        input_data = re.sub(
            configured_by_pattern, "! Last configuration change at TIME_STAMP_REPLACED", input_data
        )
        return input_data

    @staticmethod
    def _replace_crypto_strings(input_data):
        crypto_pattern = re.compile(
            r"^\s+certificate self-signed.*$\s(^\s{2}(\w+\s){1,8})+\s+quit$", flags=re.M | re.I
        )
        input_data = re.sub(crypto_pattern, "CRYPTO_REPLACED", input_data)
        return input_data

    def disable_paging(self, cls):
        cls.send_inputs("term length 0")

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_send_inputs_interact(self, setup_use_paramiko):
        interact = ["clear logg", "Clear logging buffer [confirm]", ""]
        super().test_send_inputs_interact(setup_use_paramiko, interact)

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    @pytest.mark.parametrize("priv_level", [priv for priv in PRIV_LEVELS.values()])
    def test_acquire_all_priv_levels(self, setup_use_paramiko, priv_level):
        super().test_acquire_all_priv_levels(setup_use_paramiko, priv_level)

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test__determine_current_priv_special_configuration(self, setup_use_paramiko):
        with self.platform_driver(
            **self.test_device, setup_use_paramiko=setup_use_paramiko
        ) as conn:
            conn.send_inputs(["configure terminal", "interface GigabitEthernet1"])
            current_prompt = conn.get_prompt()
            current_priv = conn._determine_current_priv(current_prompt)
        assert current_priv.name == "special_configuration"
