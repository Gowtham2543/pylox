from lox.token import Token
from lox.exception import RuntimeException

class Environment:
    def __init__(self):
        self.values = dict()

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name, value):
        self.values[name] = value
