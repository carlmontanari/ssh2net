class BaseDriverUnitTest:
    def setup_method(self):
        pass

    def get_prompt(self):
        return self.standard_prompt

    @staticmethod
    def send_inputs():
        return True

    @staticmethod
    def send_inputs_interact():
        return True

    def test__determine_current_priv_exec(self):
        assert self.driver._determine_current_priv("myrouter>") == self.privs["exec"]

    def test__determine_current_priv_privilege_exec(self):
        assert self.driver._determine_current_priv("myrouter#") == self.privs["privilege_exec"]

    def test__determine_current_priv_config(self):
        assert (
            self.driver._determine_current_priv("myrouter(config)#") == self.privs["configuration"]
        )

    def test__determine_current_priv_special_config(self):
        assert (
            self.driver._determine_current_priv("myrouter(config-if)#")
            == self.privs["special_configuration"]
        )
