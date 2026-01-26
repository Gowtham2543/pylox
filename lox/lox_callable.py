from abc import ABC

class LoxCallable(ABC):
    def call(interpreter, arguments):
        pass

    def arity():
        pass