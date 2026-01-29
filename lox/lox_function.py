from lox.lox_callable import LoxCallable
from lox.environment import Environment
from lox.exception import Return

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.closure = closure
        self.declaration = declaration

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"