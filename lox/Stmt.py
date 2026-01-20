from __future__ import annotations

from abc import ABC, abstractmethod
from lox.Expr import Expr


class stmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, expr: Stmt):
        pass

    @abstractmethod
    def visit_print_stmt(self, expr: Stmt):
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: stmtVisitor):
        pass

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expresssion: Expr):
        self.expresssion = expresssion

    def accept(self, visitor: stmtVisitor):
        return visitor.visit_print_stmt(self)

