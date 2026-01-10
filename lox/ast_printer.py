from lox.Expr import exprVisitor, Expr, Binary, Grouping, Literal, Unary
from lox.token import Token
from lox.token_type import TokenType

class ASTPrinter(exprVisitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.paranthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.paranthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"

        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.paranthesize(expr.operator.lexeme, expr.right)

    def paranthesize(self, name: str, *args: Expr):
        content = [expr.accept(self) for expr in args]
        return f"({name} {' '.join(content)})"
            