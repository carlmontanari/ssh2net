from ssh2net import SSH2Net

# Example assumes IOSXE, but should work on most platform where the command syntax below is valid!

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}

# Example with context manager:
with SSH2Net(**my_device) as conn:
    output = conn.send_inputs("show version")
    # send_inputs returns a list of results; print the zeroith result
    print(output[0])
    # native style doesn't handle privilege escalation/deescalation for you
    conn.send_inputs(["conf t", "interface loopback123", "description ssh2net was here", "end"])
    output = conn.send_inputs("show run int loopback123")
    print(output[0])
    conn.send_inputs(["conf t", "no interface loopback123", "end"])

# Example without context manager; note you need to open the shell without the context manager!
conn = SSH2Net(**my_device)
conn.open_shell()
output = conn.send_inputs("show version")
print(output[0])
conn.send_inputs(["conf t", "interface loopback123", "description ssh2net was here", "end"])
output = conn.send_inputs("show run int loopback123")
print(output[0])
conn.send_inputs(["conf t", "no interface loopback123", "end"])
