from abc import ABC

class LoxCallable(ABC):
    def call(self, interpreter, arguments):
        pass

    def arity(self):
        pass