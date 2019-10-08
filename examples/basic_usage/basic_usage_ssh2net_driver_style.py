from ssh2net.core.cisco_iosxe.driver import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}

iosxe_driver = IOSXEDriver

with IOSXEDriver(**my_device) as conn:
    output = conn.send_command("show version")
    # send_inputs returns a list of results; print the zeroith result
    print(output[0])
    conn.send_config_set(["interface loopback123", "description ssh2net was here"])
    output = conn.send_command("show run int loopback123")
    print(output[0])
    conn.send_config_set("no interface loopback123")
