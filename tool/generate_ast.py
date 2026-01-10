#!/usr/bin/env python3

from sys import argv
import os


INDENTATION = "    "


def define_type(file, base_name, class_name, fields):
    file.write(f"class {class_name}({base_name}):")
    file.write('\n')

    file.write(f"{INDENTATION}def __init__(self, {", ".join(fields)}):")
    file.write('\n')

    for field in fields:
        attr = field.split(':')[0]
        file.write(f"{INDENTATION * 2}self.{attr} = {attr}")
        file.write('\n')
    
    file.write('\n')
    file.write(f"{INDENTATION}def accept(self, visitor: {base_name.lower()}Visitor):")
    file.write('\n')
    file.write(f"{INDENTATION * 2}return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)")
    file.write('\n\n')


def define_visitor(file, base_name: str, expr_types: dict):
    file.write(f"class {base_name.lower()}Visitor(ABC):")

    for type in expr_types:
        file.write('\n')
        file.write(f"{INDENTATION}@abstractmethod")
        file.write('\n')
        file.write(f"{INDENTATION}def visit_{type.lower()}_{base_name.lower()}(self, expr: {base_name}):")
        file.write('\n')
        file.write(f'{INDENTATION * 2}pass')
        file.write('\n')


def define_ast(output_dir: str, base_name: str, expr_types: dict):
    path = os.path.join(output_dir, f"{base_name}.py")

    with open(path, mode='w') as file:
        file.write("from __future__ import annotations")
        file.write('\n\n')
        file.write("from abc import ABC, abstractmethod")
        file.write('\n')
        file.write("from lox.token import Token")
        file.write('\n\n\n')
        define_visitor(file, base_name, expr_types)
        file.write('\n\n')
        file.write(f"class {base_name}(ABC):")
        file.write('\n')
        file.write(f"{INDENTATION}@abstractmethod")
        file.write('\n')
        file.write(f"{INDENTATION}def accept(self, visitor: {base_name.lower()}Visitor):")
        file.write('\n')
        file.write(f"{INDENTATION * 2}pass")
        file.write('\n\n')

        for type in expr_types:
            class_name = type
            fields = expr_types[type]
            define_type(file, base_name, class_name, fields)


def main(args):
    if len(args) != 2:
        print("Usage: generate_ast.py <output directory>")
    
    output_dir = args[1]

    define_ast(output_dir, "Expr", {
        "Binary"   : ("left: Expr", "operator: Token", "right: Expr"),
        "Grouping" : ("expression: Expr", ),
        "Literal"  : ("value: object", ),
        "Unary"    : ("operator: Token", "right: Expr")
    })


if __name__ == "__main__":
    main(argv)
