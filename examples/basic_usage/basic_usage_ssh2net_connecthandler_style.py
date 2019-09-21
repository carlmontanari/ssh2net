from ssh2net import ConnectHandler

my_device = {"setup_host": "IP/NAME", "auth_user": "USERNAME", "auth_password": "PASSWORD"}

driver = ConnectHandler(**my_device)
output = driver.send_command("show version")
# only real difference between this style and netmiko is the output is ssh2net style
# so we print the zeroith commands result:
print(output[0][1])
driver.send_config_set(["interface loopback123", "description ssh2net was here"])
output = driver.send_command("show run int loopback123")
print(output[0][1])
driver.send_config_set("no interface loopback123")
