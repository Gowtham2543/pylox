from lox.lox_callable import LoxCallable
from lox.lox_instance import LoxInstance

class LoxClass(LoxCallable):
    def __init__(self, name, super_class, methods):
        self.name = name
        self.super_class = super_class
        self.methods = methods
    
    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
    
        if self.super_class:
            return self.super_class.find_method(name)

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self):
        initializer = self.find_method("init")
        if not initializer:
            return 0
        
        return initializer.arity()

    def __str__(self):
        return self.name