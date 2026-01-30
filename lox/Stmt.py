from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from lox.token import Token
from lox.Expr import Expr, Variable


class stmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt: Block):
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt: Class):
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression):
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt: Function):
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: If):
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: Print):
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: Return):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: Var):
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: While):
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: stmtVisitor):
        pass

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_block_stmt(self)

class Class(Stmt):
    def __init__(self, name: Token, super_class: Variable, methods: List[Function]):
        self.name = name
        self.super_class = super_class
        self.methods = methods

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_class_stmt(self)

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_expression_stmt(self)

class Function(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_function_stmt(self)

class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_if_stmt(self)

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_print_stmt(self)

class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_return_stmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_var_stmt(self)

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_while_stmt(self)

