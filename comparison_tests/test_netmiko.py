#!/usr/bin/env python
from datetime import datetime

from netmiko import ConnectHandler

from . import hosts

IOSXE_TEST = hosts.IOSXE_TEST
NXOS_TEST = hosts.NXOS_TEST
test_hosts = [IOSXE_TEST, NXOS_TEST]


def main():
    for host in test_hosts:
        commands = host.pop("test_commands")
        conn = ConnectHandler(**host)
        for command in commands:
            print(f"Sending command: '{command}'")
            print("*" * 80)
            command_start_time = datetime.now()
            r = conn.send_commands(command)
            command_end_time = datetime.now()
            print(r)
            print("*" * 80)
            print(
                f"Sending command: '{command}' took {command_end_time - command_start_time} seconds!"
            )
            print("*" * 80)
            print()


if __name__ == "__main__":
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f"Full test took {end_time - start_time} seconds!")
