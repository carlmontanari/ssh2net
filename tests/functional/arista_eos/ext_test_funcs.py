def eos_disable_paging(cls):
    cls.send_inputs("term length 0")
