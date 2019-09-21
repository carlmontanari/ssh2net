from ssh2net import SSH2Net

# Example assumes IOSXE, but should work on most platform where the command syntax below is valid!

my_device = {"setup_host": "IP/NAME", "auth_user": "USERNAME", "auth_password": "PASSWORD"}

# Example with context manager:
with SSH2Net(**my_device) as conn:
    output = conn.send_inputs("show version")
    # send_inputs returns a list of tuples where each list element is the command sent
    # and then the result as the second item in the tuple, we'll print just the result:
    print(output[0][1])
    # native style doesn't handle privilege escalation/deescalation for you
    conn.send_inputs(["conf t", "interface loopback123", "description ssh2net was here", "end"])
    output = conn.send_inputs("show run int loopback123")
    print(output[0][1])
    conn.send_inputs(["conf t", "no interface loopback123", "end"])

# Example without context manager; not you need to open the shell without the context manager!
conn = SSH2Net(**my_device)
conn.open_shell()
output = conn.send_inputs("show version")
print(output[0][1])
conn.send_inputs(["conf t", "interface loopback123", "description ssh2net was here", "end"])
output = conn.send_inputs("show run int loopback123")
print(output[0][1])
conn.send_inputs(["conf t", "no interface loopback123", "end"])
