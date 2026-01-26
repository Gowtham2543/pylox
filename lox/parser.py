from typing import List

from lox.token import Token
from lox.token_type import TokenType
from lox.Expr import Binary, Unary, Literal, Grouping, Variable, Assign, Logical, Call
from lox.Stmt import Print, Expression, Var, Block, If, While, Function


class ParserException(Exception):
    pass

class Parser:

    # expression → assigment ;
    # assignment → IDENTIFIER "=" assignment | logic_or ;
    # logic_or → logic_and ( "or" logic_and)*;
    # logic_and → equality ( "and" equality)*;
    # equality → comparison ( ( "!=" | "==" ) comparison )* ;
    # comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    # term → factor ( ( "-" | "+" ) factor )* ;
    # factor → unary ( ( "/" | "*" ) unary )* ;
    # unary → ( "!" | "-" ) unary | call ;
    # call → primary ( "(" arguments? ")" )*;
    # arguments → expression ( "," expression )*;
    # primary → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER;

    # program → declaration* EOF ;

    # declaration → funDecl | varDecl | statement ;
    # funDecl → "fun" function;
    # function → IDENTIFIER "(" parameters? ")" block;
    # varDecl → "var" IDENTIFIER ( "=" expression )? ";";
    # statement → exprStmt | forStmt | ifStmt | printStmt | whileStmt | block;
    # forStmt → "for" "(" (varDecl | exprStmt | ";") expression? ";" expression? ")" statement;    
    # ifStmt → "if" "(" expression ")" statement ( "else" statement )?;
    # whileStmt → "while" "(" expression ")" statement; 
    # block → "{" declaration "}"
    # exprStmt → expression ";" ;
    # printStmt → "print" expression ";" ;

    def __init__(self, tokens: List[Token], error_handler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.current = 0
    
    def parse(self):
        statements = []

        while not self.is_at_end():
            statements.append(self.declaration())
        
        return statements
    
    def expression(self):
        return self.assignment()

    def declaration(self):
        try:
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParserException as exc:
            self.synchronize()
    
    def statement(self):
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statements()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        
        return self.expression_statements()
    
    def for_statement(self):
        # This is just sugarized version of while loop
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match(TokenType.SEMICOLON):
            # I think this is a bad code
            pass
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statements()
        
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        # If there is condition, add the increment statement after the body
        if increment:
            body = Block([body, Expression(increment)])

        # No condition. Do infinite loop
        if not condition:
            condition = Literal(True)
        body = While(condition, body)

        # Add the initializer to the top of the body
        if initializer:
            body = Block([initializer, body])

        return body

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if'.")

        then_branch = self.statement()
        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return If(condition, then_branch, else_branch)
    
    def print_statements(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value")
        return Print(value)
    
    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after while.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition")
        body = self.statement()

        return While(condition, body)

    def expression_statements(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return Expression(expr)

    def function(self, kind):
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")

        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters = []

        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before {kind} body.")

        body = self.block()
        return Function(name, parameters, body)

    def block(self):
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def assignment(self):
        expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr
    
    def logical_or(self):
        expr = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def logical_and(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        
        return expr

    # equality -> comparison ( ("!=" | "==" ) comparison)*
    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr

    # comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )*
    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        
        return expr

    # term → factor ( ( "-" | "+" ) factor )*
    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr

    # factor → unary ( ( "/" | "*" ) unary )*
    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr
    
    # unary → ( "!" | "-" ) unary | primary
    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.call()
    
    def finish_call(self, callee):
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())

            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)
    
    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        
        return expr

    # primary → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER
    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)

        if self.match(TokenType.TRUE):
            return Literal(True)

        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ) afer expression")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression")
    
    def match(self, *token_types) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        
        return False
    
    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()

        raise self.error(self.peek(), message)
    
    def check(self, token_type) -> bool:
        if self.is_at_end():
            return False

        return self.peek().token_type == token_type       

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

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

    def error(self, token: Token, message: str):
        self.error_handler(token, message)
        return ParserException()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
        
        match self.peek().token_type:
            case TokenType.CLASS:
                pass
            case TokenType.FUN:
                pass
            case TokenType.VAR:
                pass
            case TokenType.FOR:
                pass
            case TokenType.IF:
                pass
            case TokenType.WHILE:
                pass
            case TokenType.PRINT:
                pass
            case TokenType.RETURN:
                return
            
        self.advance()
        