import time

from lox.expr import ExprVisitor, Expr
from lox.stmt import StmtVisitor
from lox.token_type import TokenType
from lox.token import Token
from lox.environment import Environment
from lox.exception import RuntimeException, Return
from lox.lox_callable import LoxCallable
from lox.lox_function import LoxFunction
from lox.lox_class import LoxClass
from lox.lox_instance import LoxInstance

class Interpreter(ExprVisitor, StmtVisitor):

    def __init__(self, error_handler):
        self.error_handler = error_handler
        self.globals       = Environment()
        self.environment   = self.globals
        self.locals        = {}

        # Create a concrete LoxCallable class for clock
        class _(LoxCallable):
            def arity(self):
                return 0

            def call(self, interpreter, arguments):
                return time.time()

            def __str__(self):
                return "<native fn>"

        self.globals.define("clock", _())

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, statement):
        statement.accept(self)

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))
    
    def visit_class_stmt(self, stmt):
        super_class = None
        if stmt.super_class:
            super_class = self.evaluate(stmt.super_class)
            if not isinstance(super_class, LoxClass):
                raise RuntimeException(stmt.super_class.name, "Superclass must be a class.")
            
        self.environment.define(stmt.name.lexeme, None)

        if stmt.super_class:
            self.environment = Environment(self.environment)
            self.environment.define("super", super_class)

        methods = {}
        for method in stmt.methods:
            function = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        
        klass = LoxClass(stmt.name.lexeme, super_class, methods)
        self.environment.assign(stmt.name, klass)
    
    def visit_get_expr(self, expr):
        object = self.evaluate(expr.object)
        if isinstance(object, LoxInstance):
            return object.get(expr.name)

        raise RuntimeException(expr.name, "Only instances have properties.")

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)

        raise Return(value)

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

        return None

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)

        if expr in self.locals:
            distance = self.locals[expr]
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

        return value

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeException as exc:
            self.error_handler(exc)

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)

                raise RuntimeException(expr.operator, "Operands must be two numbers or two strings")
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeException(expr.paren, "Can only call functions and classes.")

        # print(type(callee))
        # function = LoxCallable(callee)

        if len(arguments) != callee.arity():
            raise RuntimeException(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_set_expr(self, expr):
        object = self.evaluate(expr.object)

        if not isinstance(object, LoxInstance):
            raise RuntimeException(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        object.set(expr.name, value)

        return value
    
    def visit_super_expr(self, expr):
        distance = self.locals[expr]
        super_class = self.environment.get_at(distance, "super")
        object = self.environment.get_at(distance - 1, "this")

        method = super_class.find_method(expr.method.lexeme)

        if not method:
            raise RuntimeException(expr.method, f"Undefined property {expr.method.lexeme}.")

        return method.bind(object)

    def visit_this_expr(self, expr):
        return self.lookup_variable(expr.keyword, expr)

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)

    def visit_variable_expr(self, expr):
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name: Token, expr: Expr):
        if expr in self.locals:
            distance = self.locals[expr]
            return self.environment.get_at(distance, name.lexeme)

        return self.globals.get(name)


    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return

        raise RuntimeException(operator, "Operand must be a number")

    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return

        raise RuntimeException(operator, "Operands must be numbers")

    def is_truthy(self, object):
        if object is None:
            return False

        if isinstance(object, bool):
            return bool(object)

        return True

    def is_equal(self, a, b):
        if a is None and b is None:
            return True

        if a is None:
            return False

        return a == b

    def stringify(self, object):
        if object is None:
            return "nil"

        if isinstance(object, float):
            text = str(object)

            if text[-2:] == ".0":
                text = text[:len(text) - 2]

            return text

        return str(object)
