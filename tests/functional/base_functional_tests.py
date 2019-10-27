import pytest

import ssh2net

NET2_DIR = ssh2net.__file__
privs = None


class BaseFunctionalTest:
    def setup_method(self):
        pass

    @staticmethod
    def _replace_trailing_chars_running_config(input_data):
        return input_data

    @staticmethod
    def _replace_config_bytes(input_data):
        return input_data

    @staticmethod
    def _replace_timestamps(input_data):
        return input_data

    @staticmethod
    def _replace_configured_by(input_data):
        return input_data

    @staticmethod
    def _replace_crypto_strings(input_data):
        return input_data

    def clean_input_data(self, input_data):
        input_data = self._replace_trailing_chars_running_config(input_data)
        input_data = self._replace_config_bytes(input_data)
        input_data = self._replace_timestamps(input_data)
        input_data = self._replace_configured_by(input_data)
        input_data = self._replace_crypto_strings(input_data)
        return input_data

    def disable_paging(self, cls):
        # implement platform specific disable paging string function here
        pass

    def show_run_execute(self):
        conn = ssh2net.SSH2Net(**self.test_device)
        show_run = conn.open_and_execute("show run")
        show_run = self.clean_input_data(show_run)
        return show_run

    def show_run_inputs(self, setup_use_paramiko, command):
        with ssh2net.SSH2Net(**self.test_device, setup_use_paramiko=setup_use_paramiko) as conn:
            show_run = conn.send_inputs(command)[0]
        show_run = self.clean_input_data(show_run)
        return show_run

    def show_run_inputs_no_strip_prompt(self, setup_use_paramiko, command):
        with ssh2net.SSH2Net(**self.test_device, setup_use_paramiko=setup_use_paramiko) as conn:
            show_run = conn.send_inputs(command, strip_prompt=False)[0]
        show_run = self.clean_input_data(show_run)
        return show_run

    def _send_inputs_interact(self, setup_use_paramiko, interact, **kwargs):
        with ssh2net.SSH2Net(**self.test_device, setup_use_paramiko=setup_use_paramiko) as conn:
            try:
                current_prompt = interact[3]
            except IndexError:
                current_prompt = conn.get_prompt()
            interactive = conn.send_inputs_interact(
                (interact[0], interact[1], interact[2], current_prompt), **kwargs
            )[0]
        return interactive

    def _disable_paging_function(self, setup_use_paramiko):
        with ssh2net.SSH2Net(
            **self.test_device,
            setup_use_paramiko=setup_use_paramiko,
            comms_disable_paging=self.disable_paging,
        ) as conn:
            show_run = conn.send_inputs("show run")[0]
        show_run = self.clean_input_data(show_run)
        return show_run

    def _disable_paging_external_function(self, setup_use_paramiko):
        with ssh2net.SSH2Net(
            **self.test_device,
            setup_use_paramiko=setup_use_paramiko,
            comms_disable_paging=self.disable_paging_ext_function,
        ) as conn:
            show_run = conn.send_inputs("show run")[0]
        show_run = self.clean_input_data(show_run)
        return show_run

    def test_show_run_execute(self):
        with open(f"{self.func_test_dir}expected_output/show_run_execute", "r") as f:
            expected_show_run = f.read().strip()
        expected_show_run = self.clean_input_data(expected_show_run)
        show_run = self.show_run_execute()
        assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
        assert show_run == expected_show_run

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_show_run_inputs(self, setup_use_paramiko, command="show run"):
        with open(f"{self.func_test_dir}expected_output/show_run", "r") as f:
            expected_show_run = f.read()
        expected_show_run = self.clean_input_data(expected_show_run)
        show_run = self.show_run_inputs(setup_use_paramiko, command)
        assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
        assert show_run == expected_show_run

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_show_run_inputs_no_strip_prompt(self, setup_use_paramiko, command="show run"):
        with open(f"{self.func_test_dir}expected_output/show_run", "r") as f:
            expected_show_run = f.read()
        expected_show_run = self.clean_input_data(expected_show_run)
        show_run = self.show_run_inputs(setup_use_paramiko, command)
        assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
        assert show_run == expected_show_run

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_send_inputs_interact(self, setup_use_paramiko, interact, clean=False, **kwargs):
        with open(f"{self.func_test_dir}expected_output/interactive", "r") as f:
            expected_interactive = f.read().strip()
        interactive = self._send_inputs_interact(setup_use_paramiko, interact, **kwargs)
        if clean:
            expected_interactive = self.clean_input_data(expected_interactive)
            interactive = self.clean_input_data(interactive)
        assert len(interactive.splitlines()) == len(expected_interactive.splitlines())
        assert interactive == expected_interactive

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_disable_paging_function(self, setup_use_paramiko):
        with open(f"{self.func_test_dir}expected_output/show_run", "r") as f:
            expected_show_run = f.read()
        expected_show_run = self.clean_input_data(expected_show_run)
        show_run = self._disable_paging_function(setup_use_paramiko)
        assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
        assert show_run == expected_show_run

    @pytest.mark.parametrize("setup_use_paramiko", [False, True], ids=["ssh2", "paramiko"])
    def test_disable_paging_external_function(self, setup_use_paramiko):
        with open(f"{self.func_test_dir}expected_output/show_run", "r") as f:
            expected_show_run = f.read()
        expected_show_run = self.clean_input_data(expected_show_run)
        show_run = self._disable_paging_external_function(setup_use_paramiko)
        assert len(show_run.splitlines()) == len(expected_show_run.splitlines())
        assert show_run == expected_show_run

    def test_acquire_all_priv_levels(self, setup_use_paramiko, priv_level):
        if not priv_level.requestable:
            pytest.skip(f"priv level {priv_level.name} is not requestable by ssh2net")
        with self.platform_driver(
            **self.test_device, setup_use_paramiko=setup_use_paramiko
        ) as conn:
            conn.attain_priv(priv_level.name)
            current_prompt = conn.get_prompt()
            current_priv = conn._determine_current_priv(current_prompt)
            assert current_priv.name == priv_level.name
