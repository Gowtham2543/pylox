#!/usr/bin/env python3

import os
from sys import argv
from typing import Tuple


INDENTATION = "    "

COMMON_IMPORTS = ("from __future__ import annotations\n",
                   "from abc import ABC, abstractmethod",
                   "from typing import List\n")


EXPRESSION_IMPORTS = COMMON_IMPORTS + (
    "from lox.token import Token",
)

STATEMENTS_IMPORTS = COMMON_IMPORTS + (
    "from lox.token import Token",
    "from lox.expr import Expr, Variable",
)


def define_type(file, base_name, class_name, fields):
    file.write(f"class {class_name}({base_name.title()}):")
    file.write('\n')

    file.write(f"{INDENTATION}def __init__(self, {', '.join(fields)}):")
    file.write('\n')

    for field in fields:
        attr = field.split(':')[0]
        file.write(f"{INDENTATION * 2}self.{attr} = {attr}")
        file.write('\n')

    file.write('\n')
    file.write(f"{INDENTATION}def accept(self, visitor: {base_name.title()}Visitor):")
    file.write('\n')
    file.write(f"{INDENTATION * 2}return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)")
    file.write('\n\n')


def define_visitor(file, base_name: str, expr_types: dict):
    file.write(f"class {base_name.title()}Visitor(ABC):")

    for type in expr_types:
        file.write('\n')
        file.write(f"{INDENTATION}@abstractmethod")
        file.write('\n')
        file.write(f"{INDENTATION}def visit_{type.lower()}_{base_name.lower()}(self, {base_name.lower()}: {type}):")
        file.write('\n')
        file.write(f'{INDENTATION * 2}pass')
        file.write('\n')


def define_imports(file, imports):
    file.write('\n'.join(imports))


def define_ast(output_dir: str, base_name: str, expr_types: dict, imports: Tuple[str, ...]):
    path = os.path.join(output_dir, f"{base_name}.py")

    with open(path, mode='w') as file:
        define_imports(file, imports)
        file.write('\n\n\n')
        define_visitor(file, base_name, expr_types)
        file.write('\n\n')
        file.write(f"class {base_name.title()}(ABC):")
        file.write('\n')
        file.write(f"{INDENTATION}@abstractmethod")
        file.write('\n')
        file.write(f"{INDENTATION}def accept(self, visitor: {base_name.title()}Visitor):")
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

    define_ast(output_dir, "expr", {
        "Assign"   : ("name: Token", "value: Expr"),
        "Binary"   : ("left: Expr", "operator: Token", "right: Expr"),
        "Call"     : ("callee: Expr", "paren: Token", "arguments: List[Expr]"),
        "Get"      : ("object: Expr", "name: Token"),
        "Grouping" : ("expression: Expr", ),
        "Literal"  : ("value: object", ),
        "Logical"  : ("left: Expr", "operator: Token", "right: Expr"),
        "Set"      : ("object: Expr", "name: Token", "value: Expr"),
        "Super"    : ("keyword: Token", "method: Token"),
        "This"     : ("keyword: Token", ),
        "Unary"    : ("operator: Token", "right: Expr"),
        "Variable" : ("name: Token", )
    },
    EXPRESSION_IMPORTS)

    define_ast(output_dir, "stmt", {
        "Block"      : ("statements: List[Stmt]", ),
        "Class"      : ("name: Token", "super_class: Variable", "methods: List[Function]"),
        "Expression" : ("expression: Expr", ),
        "Function"   : ("name: Token", "params: List[Token]", "body: List[Stmt]"),
        "If"         : ("condition: Expr", "then_branch: Stmt", "else_branch: Stmt"),
        "Print"      : ("expression: Expr", ),
        "Return"     : ("keyword: Token", "value: Expr"),
        "Var"        : ("name: Token", "initializer: Expr"),
        "While"      : ("condition: Expr", "body: Stmt")
    },
    STATEMENTS_IMPORTS)


if __name__ == "__main__":
    main(argv)
