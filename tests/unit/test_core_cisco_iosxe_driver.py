from ssh2net.core.cisco_iosxe.driver import IOSXEDriver, PRIVS


class MockSSH2Net:
    def get_prompt(self):
        return "myrouter#"

    def send_inputs(self):
        return True

    def send_inputs_interact(self):
        return True


def test__determine_current_priv_iosxe_exec():
    driver = IOSXEDriver()
    assert driver._determine_current_priv("myrouter>") == PRIVS["exec"]


def test__determine_current_priv_iosxe_privilege_exec():
    driver = IOSXEDriver()
    assert driver._determine_current_priv("myrouter#") == PRIVS["privilege_exec"]


def test__determine_current_priv_iosxe_config():
    driver = IOSXEDriver()
    assert driver._determine_current_priv("myrouter(config)#") == PRIVS["configuration"]


def test__determine_current_priv_iosxe_special_config():
    driver = IOSXEDriver()
    assert driver._determine_current_priv("myrouter(config-if)#") == PRIVS["special_configuration"]
