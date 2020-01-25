from ssh2net import ConnectHandler

my_device = {
    "device_type": "cisco_xe",
    "host": "172.18.0.11",
    "username": "vrnetlab",
    "password": "VR-netlab9",
}

driver = ConnectHandler(**my_device)
output = driver.send_commands("show version")
# send_inputs returns a list of result objects; print the zeroith result
print(output[0].result)
driver.send_configs(["interface loopback123", "description ssh2net was here"])
output = driver.send_commands("show run int loopback123")
print(output[0].result)
driver.send_configs("no interface loopback123")

# or use "normal" netmiko methods
output = driver.send_command("show version")
print(output)
