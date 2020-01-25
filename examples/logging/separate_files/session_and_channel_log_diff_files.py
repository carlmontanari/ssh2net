import logging

from ssh2net import SSH2Net

# Set desired log format
log_format = "%(asctime)s [%(levelname)s] in %(pathname)s:%(lineno)d \n\t %(message)s"

# Setup session logging; session logging is connection stuff only -- i.e. socket/session/channel
session_log_file = "session.log"
# Set the "ssh2net_session" logger
session_logger = logging.getLogger("ssh2net_session")
# Set log level to level of your choice
session_logger.setLevel(logging.DEBUG)
session_logger_file_handler = logging.FileHandler(session_log_file)
# Assign formatter to log handler
session_logger_file_handler.setFormatter(logging.Formatter(log_format))
# Add log handler to the session_logger
session_logger.addHandler(session_logger_file_handler)
# Do not propagate logs to stdout
session_logger.propagate = False

# Repeat similar steps as above for channel logger; channel logger captures reads/writes
# ssh2net_channel logger removes duplicate entries from the log to avoid logs being massive
channel_log_file = "channel.log"
channel_logger = logging.getLogger("ssh2net_channel")
channel_logger.setLevel(logging.DEBUG)
channel_logger_file_handler = logging.FileHandler(channel_log_file)
channel_logger_file_handler.setFormatter(logging.Formatter(log_format))
channel_logger.addHandler(channel_logger_file_handler)
channel_logger.propagate = False

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
with SSH2Net(**my_device) as conn:
    show_run = conn.send_inputs("show run")

print(show_run[0].result)
