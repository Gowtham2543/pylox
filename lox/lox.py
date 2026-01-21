from pathlib import Path

from lox.scanner import Scanner
from lox.token import Token
from lox.token_type import TokenType
from lox.parser import Parser
from lox.ast_printer import ASTPrinter
from lox.interpreter import Interpreter


class Lox:
    had_error = False
    had_runtime_error = False
    interpreter = None

    @classmethod
    def get_interpreter(cls):
        if cls.interpreter is None:
            cls.interpreter = Interpreter(cls.runtime_error)
        return cls.interpreter

    @staticmethod
    def run_prompt():
        while True:
            print('>', end = ' ')
            line = input()

            if not line:
                break
        
            Lox.run(line)

    @staticmethod
    def run(source):
        scanner = Scanner(source, Lox.line_error)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, Lox.token_error)
        statements = parser.parse()

        if Lox.had_error:
            return

        # In a REPL every time the interpreter object will be intialized, deleting the environment,
        # which is wrong
        # interpreter = Interpreter(Lox.runtime_error)
        interpreter = Lox.get_interpreter()
        interpreter.interpret(statements)
    
    @staticmethod
    def run_file(path):
        source = Path(path).read_text()
        Lox.run(source)

        if Lox.had_error:
            exit(65)
        
        if Lox.had_runtime_error:
            exit(70)

    @staticmethod
    def line_error(line, message):
        Lox.report(line, "", message)

    @staticmethod
    def token_error(token: Token, message: str):
        if token.token_type == TokenType.EOF:
            Lox.report(token.line, " at the end", message)
        else:
            Lox.report(token.line, f"at '{token.lexeme}'", message)

    @staticmethod
    def report(line, where, message):
        print(f'[line {line}] Error {where} : {message}' )
        Lox.had_error = True
    
    @staticmethod
    def runtime_error(error):
        print(f"{str(error)}\n[line {error.token.line}]")
        Lox.had_runtime_error = True
