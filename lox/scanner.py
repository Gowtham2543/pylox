from lox.token_type import TokenType
from lox.token import Token


KEYWORDS = {
    "and"    : TokenType.AND,
    "class"  : TokenType.CLASS,
    "else"   : TokenType.ELSE,
    "false"  : TokenType.FALSE,
    "for"    : TokenType.FOR,
    "fun"    : TokenType.FUN,
    "if"     : TokenType.IF,
    "nil"    : TokenType.NIL,
    "or"     : TokenType.OR,
    "print"  : TokenType.PRINT,
    "return" : TokenType.RETURN,
    "super"  : TokenType.SUPER,
    "this"   : TokenType.THIS,
    "true"   : TokenType.TRUE,
    "var"    : TokenType.VAR,
    "while"  : TokenType.WHILE
}


class Scanner:
    def __init__(self, source, error_handler):
        self.source = source
        self.error_handler = error_handler

        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        
    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens 

    def scan_token(self):
        char = self.advance()
        match char:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
            case '{':
                self.add_token(TokenType.LEFT_BRACE)
            case '}':
                self.add_token(TokenType.RIGHT_BRACE)
            case ',':
                self.add_token(TokenType.COMMA)
            case '.':
                self.add_token(TokenType.DOT)
            case '-':
                self.add_token(TokenType.MINUS)
            case '+':
                self.add_token(TokenType.PLUS)
            case ';':
                self.add_token(TokenType.SEMICOLON)
            case '*':
                self.add_token(TokenType.STAR)
            case '!':
                self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    # Comment goes until the end of the line
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass
            case '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string()
            case _:
                if self.is_digit(char):
                    self.number()
                elif self.is_alpha(char):
                    self.identifier()
                else:
                    self.error_handler(self.line, "Unexpected Chanracer.")
    
    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        
        text = self.source[self.start:self.current]
        type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            self.error_handler(self.line, "Unterminated string.")
            return
        
        # Closing "
        self.advance()

        # Trim the surrounding quotes
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        
        # Look for fraction
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()
        
        while self.is_digit(self.peek()):
            self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def match(self, expected: str):
        if self.is_at_end():
            return False
        
        if self.source[self.current] != expected:
            return False

        # Only consume when expected character is found
        self.current += 1
        return True
    
    def peek(self):
        '''
        Peek at the next character without moving the current
        '''
        if self.is_at_end():
            return '\0'
        
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'

        return self.source[self.current + 1]

    def is_alpha(self, c: str):
        return (ord('a') <= ord(c) <= ord('z') or
                ord('A') <= ord(c) <= ord('Z') or
                c == '_')

    def is_digit(self, c: str):
        return ord('0') <= ord(c) <= ord('9')
    
    def is_alpha_numeric(self, c: str):
        return self.is_alpha(c) or self.is_digit(c)
    
    def advance(self):
        '''
        Return the current character and move the current by 1
        '''
        self.current += 1
        return self.source[self.current - 1]
        
    def add_token(self, token_type: TokenType, literal: object | None = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
        
    def is_at_end(self):
        return self.current >= len(self.source)
