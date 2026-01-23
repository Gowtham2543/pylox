from sys import argv
from lox.lox import Lox

def main(args):
    if len(args) > 2:
        print('Usage : jlox [script]')
        exit(64)
    elif len(args) == 2:
        Lox.run_file(args[1])
    else:
        Lox.run_prompt()

main(argv)