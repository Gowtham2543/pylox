from lox.token import Token
from lox.exception import RuntimeException

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    
    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)

        raise RuntimeException(name, f"Undefined property {name.lexeme}.")

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value
    
    def __str__(self):
        return self.klass.name  + " instance"