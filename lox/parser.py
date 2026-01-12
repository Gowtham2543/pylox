from lox.token import Token
from lox.token_type import TokenType
from lox.Expr import Binary

class Parser:

    # expression → equality ;
    # equality → comparison ( ( "!=" | "==" ) comparison )* ;
    # comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    # term → factor ( ( "-" | "+" ) factor )* ;
    # factor → unary ( ( "/" | "*" ) unary )* ;
    # unary → ( "!" | "-" ) unary | primary ;
    # primary → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" ;

    def __init__(self, tokens: Token):
        self.tokens = tokens
        self.current = 0
    
    def expression(self):
        self.equality()
    
    # equality -> comparison ( ("!=" | "==" ) comparison)*
    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def match(self, *token_types) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        
        return False
    
    def check(self, token_type) -> bool:
        if self.is_at_end():
            return False

        return self.peek() == token_type       

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek() == TokenType.EOF

    def peek(self):
        """
        Next token to be consumed
        """
        return self.tokens[self.current]

    def previous(self):
        """
        Recently consumed token
        """
        return self.tokens[self.current - 1]
