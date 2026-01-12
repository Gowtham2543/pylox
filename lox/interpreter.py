from lox.Expr import exprVisitor
from lox.token import TokenType


class RuntimeException(Exception):
    def __init__(self, token, message):
        self.token = token
        super().__init__(f"{message}")


class Interpreter(exprVisitor):

    def __init__(self, error_handler):
        self.error_handler = error_handler

    def evaluate(self,expr):
        return expr.accept(self)
    
    def interpret(self, expressions):
        try:
            val = self.evaluate(expressions)
            print(self.stringify(val))
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
                return not self.is_equal(left, right)
    
    def visit_literal_expr(self, expr):
        return expr.value
    
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
                text = text[len(text) - 2]
        
            return text
        
        return str(object)
    