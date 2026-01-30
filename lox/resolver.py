from enum import Enum

from lox.Expr import exprVisitor
from lox.Stmt import stmtVisitor
from lox.token import Token


class FunctionType(Enum):
    NONE = "None"
    FUNCTION = "FUNCTION"
    INITIALIZER = "INITIALIZER"
    METHOD = "METHOD"


class ClassType(Enum):
    NONE = "None"
    CLASS = "CLASS"


class Resolver(exprVisitor, stmtVisitor):
    def __init__(self, interpreter, error_handler):
        self.interpreter = interpreter
        self.scopes = []
        self.stack = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
        self.error_handler = error_handler

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.end_scope()
    
    def visit_class_stmt(self, stmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER

            self.resolve_function(method, declaration)
        
        self.end_scope()
        self.current_class = enclosing_class
    
    def visit_get_expr(self, expr):
        self.resolve_expr(expr.object)

    def visit_expression_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_if_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)

        if stmt.else_branch:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt):
        if self.current_function == FunctionType.NONE:
            self.error_handler(stmt.keyword, "Can't return from top-level code.")

        if stmt.value:
            if self.current_function == FunctionType.INITIALIZER:
                self.error_handler(stmt.keyword, "Can't return a value from an initializer.")
                
            self.resolve_expr(stmt.value)

    def visit_while_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmts(stmt.body)

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)

        if stmt.initializer:
            self.resolve_expr(stmt.initializer)

        self.define(stmt.name)

    def visit_assign_expr(self, expr):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expr(self, expr):
        self.resolve_expr(expr.callee)

        for argument in expr.arguments:
            self.resolve_expr(argument)

    def visit_grouping_expr(self, expr):
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr):
        pass

    def visit_logical_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
    
    def visit_set_expr(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)
    
    def visit_this_expr(self, expr):
        if self.current_class == ClassType.NONE:
            self.error_handler(expr.keyword, "Can't use 'this' outside of a class.")

        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr):
        self.resolve_expr(expr.right)

    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_variable_expr(self, expr):
        if self.scopes and expr.name.lexeme in self.scopes[-1] and self.scopes[-1][expr.name.lexeme] == False:
            self.error_handler(expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)

    def resolve_statements(self, statements):
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, stmt):
        stmt.accept(self)

    def resolve_expr(self, expr):
        expr.accept(self)

    def resolve_function(self, function, function_type):
        enclosing_function = self.current_function
        self.current_function = function_type

        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve_statements(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.error_handler(name, "Already variable with this name in this scope.")

        self.scopes[-1][name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        scope_length = len(self.scopes)
        for i in range(scope_length - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, scope_length - 1 - i)
                return