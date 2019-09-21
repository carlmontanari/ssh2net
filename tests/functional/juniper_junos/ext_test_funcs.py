def junos_disable_paging(cls):
    cls.send_inputs("set cli screen-length 0")
