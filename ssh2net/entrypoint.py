from ssh2net.channel import SSH2NetChannel


class SSH2NetBase(SSH2NetChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
