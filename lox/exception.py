class ParserException(Exception):
    pass


class RuntimeException(Exception):
    def __init__(self, token, message):
        self.token = token
        super().__init__(f"{message}")


class Return(RuntimeError):
    def __init__(self, value):
        super().__init__()
        self.value = value
