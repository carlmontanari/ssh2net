from ssh2net.core.cisco_iosxe.driver import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}


with IOSXEDriver(**my_device) as conn:
    output = conn.send_commands("show version")
    # as ssh2net always returns a list of result objects, pass the zeroith element of the output
    output = conn.textfsm_parse_output("show version", output[0].result)
    print(output)
