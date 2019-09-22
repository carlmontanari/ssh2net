IOSXE_TEST = {
    "host": "172.18.0.11",
    "username": "vrnetlab",
    "password": "VR-netlab9",
    "device_type": "cisco_xe",
    "test_commands": ["show run", "show version"],
}

NXOS_TEST = {
    "host": "172.18.0.12",
    "username": "vrnetlab",
    "password": "VR-netlab9",
    "device_type": "cisco_nxos",
    "test_commands": ["show run", "show version"],
}

# need to get cisco_iosxr image in vrnetlab for testing
# IOSXR_TEST = {
#    "host": "172.18.0.13",
#    "username": "vrnetlab",
#    "password": "VR-netlab9",
#    "device_type": "cisco_iosxr",
#    "test_commands": ["show run", "show version"],
# }

# need to get arista_eos image in vrnetlab for testing + fix libssh2 keyboard interactive auth issue
# EOS_TEST = {
#    "host": "172.18.0.14",
#    "username": "vrnetlab",
#    "password": "VR-netlab9",
#    "device_type": "arista_eos",
#    "test_commands": ["show run", "show version"],
# }

JUNOS_TEST = {
    "host": "172.18.0.15",
    "username": "vrnetlab",
    "password": "VR-netlab9",
    "device_type": "juniper_junos",
    "test_commands": ["show configuration", "show version"],
}
