from ssh2net.core.cisco_iosxe.driver import IOSXEDriver

my_device = {
    "setup_host": "IP/NAME",
    "auth_user": "USERNAME",
    "auth_public_key": "/PATH/TO/KEY/TO/USE",
}


with IOSXEDriver(**my_device) as conn:
    output = conn.send_commands("show version")
    print(output[0].result)
    conn.send_configs(["interface loopback123", "description ssh2net was here"])
    output = conn.send_commands("show run int loopback123")
    print(output[0].result)
    conn.send_configs("no interface loopback123")
