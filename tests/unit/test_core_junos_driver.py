from ssh2net.core.juniper_junos.driver import JunosDriver, PRIVS


class MockSSH2Net:
    def get_prompt(self):
        return "mysrx#"

    def send_inputs(self):
        return True

    def send_inputs_interact(self):
        return True


def test__determine_current_priv_iosxe_exec():
    conn = MockSSH2Net
    driver = JunosDriver(conn)
    assert driver._determine_current_priv("mysrx>") == PRIVS["exec"]


def test__determine_current_priv_iosxe_privilege_exec():
    conn = MockSSH2Net
    driver = JunosDriver(conn)
    assert driver._determine_current_priv("mysrx#") == PRIVS["configuration"]
