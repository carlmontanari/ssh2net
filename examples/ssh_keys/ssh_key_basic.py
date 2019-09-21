from ssh2net import SSH2Net
from ssh2net.core.cisco_iosxe.driver import IOSXEDriver

my_device = {
    "setup_host": "IP/NAME",
    "auth_user": "USERNAME",
    "auth_public_key": "/PATH/TO/KEY/TO/USE",
}

iosxe_driver = IOSXEDriver

with SSH2Net(**my_device) as conn:
    driver = iosxe_driver(conn)
    output = driver.send_command("show version")
    print(output[0][1])
    driver.send_config_set(["interface loopback123", "description ssh2net was here"])
    output = driver.send_command("show run int loopback123")
    print(output[0][1])
    driver.send_config_set("no interface loopback123")
