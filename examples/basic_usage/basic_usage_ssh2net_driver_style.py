from ssh2net import SSH2Net
from ssh2net.core.cisco_iosxe.driver import IOSXEDriver

my_device = {"setup_host": "IP/NAME", "auth_user": "USERNAME", "auth_password": "PASSWORD"}

iosxe_driver = IOSXEDriver

with SSH2Net(**my_device) as conn:
    driver = iosxe_driver(conn)
    output = driver.send_command("show version")
    # send_inputs returns a list of results; print the zeroith result
    print(output[0])
    driver.send_config_set(["interface loopback123", "description ssh2net was here"])
    output = driver.send_command("show run int loopback123")
    print(output[0])
    driver.send_config_set("no interface loopback123")