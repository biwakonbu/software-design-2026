"""Runnable starter: explain why the AST is Binary before adding a new operator."""
from calculator import calculate, parse
if __name__ == '__main__':
    expression = '2 + 3 * 4'
    print(parse(expression))
    print(calculate(expression))
