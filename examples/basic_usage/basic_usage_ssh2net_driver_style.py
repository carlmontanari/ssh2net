from ssh2net.core.cisco_iosxe.driver import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}

iosxe_driver = IOSXEDriver

with IOSXEDriver(**my_device) as conn:
    output = conn.send_commands("show version")
    # send_inputs returns a list of result objects; print the zeroith result
    print(output[0].result)
    conn.send_configs(["interface loopback123", "description ssh2net was here"])
    output = conn.send_commands("show run int loopback123")
    print(output[0].result)
    conn.send_configs("no interface loopback123")
