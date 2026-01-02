from pathlib import Path

from lox.scanner import Scanner

class Lox:
    had_error = False

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
        scanner = Scanner(source, Lox.error)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)
    
    @staticmethod
    def run_file(path):
        source = Path(path).read_text()
        Lox.run(source)

        if Lox.had_error:
            exit(65)

    @staticmethod
    def error(line, message):
        Lox.report(line, "", message)

    @staticmethod
    def report(line, where, message):
        print(f'[line {line}] Error {where} : {message}' )
        Lox.had_error = True
