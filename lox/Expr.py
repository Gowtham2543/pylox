from __future__ import annotations

from abc import ABC, abstractmethod
from lox.token import Token


class exprVisitor(ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Expr):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Expr):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Expr):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Expr):
        pass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: exprVisitor):
        pass

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: exprVisitor):
        return visitor.visit_binary_expr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: exprVisitor):
        return visitor.visit_grouping_expr(self)

class Literal(Expr):
    def __init__(self, Value: object):
        self.Value = Value

    def accept(self, visitor: exprVisitor):
        return visitor.visit_literal_expr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: exprVisitor):
        return visitor.visit_unary_expr(self)

