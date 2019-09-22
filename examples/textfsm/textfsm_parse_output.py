from ssh2net import SSH2Net
from ssh2net.core.cisco_iosxe.driver import IOSXEDriver

my_device = {"setup_host": "IP/NAME", "auth_user": "USERNAME", "auth_password": "PASSWORD"}

iosxe_driver = IOSXEDriver

with SSH2Net(**my_device) as conn:
    driver = iosxe_driver(conn)
    output = driver.send_command("show version")
    # as ssh2net always returns a list of outputs, pass the zeroith element of the output
    output = driver.textfsm_parse_output("show version", output[0])
    print(output)
