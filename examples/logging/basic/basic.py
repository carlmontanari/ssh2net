import logging

from ssh2net import SSH2NetBase

logging.basicConfig(filename="ssh2net.log", level=logging.DEBUG)
logger = logging.getLogger("ssh2net")


my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
with SSH2NetBase(**my_device) as conn:
    show_run = conn.send_inputs("show run")

print(show_run[0].result)
