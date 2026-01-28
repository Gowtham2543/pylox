from lox.Expr import exprVisitor
from lox.Stmt import stmtVisitor
from lox.token import Token

class Resolver(exprVisitor, stmtVisitor):
    def __init__(self, interpreter, error_handler):
        self.interpreter = interpreter
        self.scopes = []
        self.stack = []
        self.error_handler = error_handler
    
    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.end_scope()
    
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
        if stmt.value:
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
    
    def visit_unary_expr(self, expr):
        self.resolve_expr(expr.right)
    
    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        
        self.resolve_function(stmt)

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
    
    def resolve_function(self, function):
        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolve_statements(function.body)
        self.end_scope()

    def begin_scope(self):
        self.scopes.append({})
    
    def end_scope(self):
        self.scopes.pop()
    
    def declare(self, name):
        if not self.scopes:
            return
        
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