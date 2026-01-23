from lox.token import Token
from lox.exception import RuntimeException

class Environment:
    def __init__(self, enclosing: Environment | None = None):
        self.values = dict()
        self.enclosing = enclosing

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.enclosing:
            return self.enclosing.get(name)
        
        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")
    
    def assign(self, name: Token, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name, value):
        self.values[name] = value
