class RuntimeException(Exception):
    def __init__(self, token, message):
        self.token = token
        super().__init__(f"{message}")