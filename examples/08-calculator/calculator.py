"""Reference: tokenize -> recursive-descent AST -> explicit evaluation. No eval()."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import re
import sys

class CalculatorError(Exception):
    """A user-facing lexical, syntax, or semantic error."""

@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    offset: int

@dataclass(frozen=True)
class Number:
    value: float

@dataclass(frozen=True)
class Unary:
    op: str
    operand: object

@dataclass(frozen=True)
class Binary:
    op: str
    left: object
    right: object

def tokenize(source: str) -> list[Token]:
    tokens = []
    pos = 0
    while pos < len(source):
        if source[pos].isspace():
            pos += 1
            continue
        match = re.match(r'(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)', source[pos:])
        if match:
            text = match.group()
            tokens.append(Token('number', text, pos))
            pos += len(text)
        elif source[pos] in '+-*/()':
            tokens.append(Token(source[pos], source[pos], pos))
            pos += 1
        else:
            raise CalculatorError(f'lexical error at column {pos + 1}: {source[pos]!r}')
    tokens.append(Token('eof', '', pos))
    return tokens

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens, self.pos = tokens, 0
    @property
    def current(self):
        return self.tokens[self.pos]
    def take(self):
        token = self.current
        self.pos += 1
        return token
    def expression(self):
        node = self.term()
        while self.current.kind in ('+', '-'):
            node = Binary(self.take().kind, node, self.term())
        return node
    def term(self):
        node = self.factor()
        while self.current.kind in ('*', '/'):
            node = Binary(self.take().kind, node, self.factor())
        return node
    def factor(self):
        token = self.take()
        if token.kind == 'number':
            return Number(float(token.text))
        if token.kind in ('+', '-'):
            return Unary(token.kind, self.factor())
        if token.kind == '(':
            node = self.expression()
            if self.current.kind != ')':
                raise CalculatorError(f'syntax error at column {self.current.offset + 1}: expected )')
            self.take()
            return node
        raise CalculatorError(f'syntax error at column {token.offset + 1}: expected number or (')

def parse(source: str):
    parser = Parser(tokenize(source))
    node = parser.expression()
    if parser.current.kind != 'eof':
        raise CalculatorError(f'syntax error at column {parser.current.offset + 1}: unexpected token')
    return node

def evaluate(node):
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Unary):
        if node.op not in ('+', '-'): raise CalculatorError('semantic error: unknown unary operator')
        value = evaluate(node.operand)
        return value if node.op == '+' else -value
    if isinstance(node, Binary):
        left, right = evaluate(node.left), evaluate(node.right)
        if node.op == '+': return left + right
        if node.op == '-': return left - right
        if node.op == '*': return left * right
        if node.op != '/': raise CalculatorError('semantic error: unknown binary operator')
        if right == 0: raise CalculatorError('semantic error: division by zero')
        return left / right
    raise CalculatorError('semantic error: unknown AST node')

def calculate(source: str):
    return evaluate(parse(source))

def main(argv=None):
    parser = argparse.ArgumentParser(description='Explicit AST calculator')
    parser.add_argument('--eval', metavar='EXPRESSION', required=True)
    args = parser.parse_args(argv)
    try:
        result = calculate(args.eval)
        print(int(result) if result.is_integer() else result)
        return 0
    except (CalculatorError, RecursionError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
