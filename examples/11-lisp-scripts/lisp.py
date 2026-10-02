"""Runnable reference interpreter. Python 3.12+, standard library only."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import math
import re

STAGE = 11

class LispError(Exception):
    """Errors in source programs, never a Python traceback for expected mistakes."""

class Symbol(str):
    """Keep symbols distinct from string literals."""

@dataclass(frozen=True)
class Token:
    text: str
    offset: int
    string: bool = False

def tokenize(source):
    tokens, pos = [], 0
    while pos < len(source):
        char = source[pos]
        if char.isspace():
            pos += 1
        elif char == ';':
            end = source.find('\n', pos)
            pos = len(source) if end == -1 else end + 1
        elif char in "()'":
            tokens.append(Token(char, pos))
            pos += 1
        elif char == '"':
            start, pos, value = pos, pos + 1, ''
            while pos < len(source) and source[pos] != '"':
                if source[pos] == '\\':
                    pos += 1
                    if pos == len(source):
                        raise LispError(f'read error at offset {start}: unfinished escape')
                    escapes = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\'}
                    if source[pos] not in escapes:
                        raise LispError(f'read error at offset {pos}: unknown escape')
                    value += escapes[source[pos]]
                else:
                    value += source[pos]
                pos += 1
            if pos == len(source):
                raise LispError(f'read error at offset {start}: unclosed string')
            tokens.append(Token(value, start, True))
            pos += 1
        else:
            start = pos
            while pos < len(source) and not source[pos].isspace() and source[pos] not in "()';\"":
                pos += 1
            tokens.append(Token(source[start:pos], start))
    return tokens

def atom(token):
    if token.string: return token.text
    if token.text == '#t': return True
    if token.text == '#f': return False
    # Recognize numeric syntax before conversion: a conversion failure must not
    # turn a numeric literal into an unknown symbol.
    if re.fullmatch(r'[+-]?[0-9]+', token.text):
        try: return int(token.text)
        except ValueError:
            raise LispError('read error: integer literal exceeds host conversion limit') from None
    if re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?', token.text):
        try: value = float(token.text)
        except (ValueError, OverflowError):
            raise LispError('read error: numeric literal exceeds host conversion range') from None
        if not math.isfinite(value):
            raise LispError('read error: numeric literal must be finite')
        return value
    return Symbol(token.text)

def read_all(source):
    tokens, pos = tokenize(source), 0
    def read():
        nonlocal pos
        if pos >= len(tokens): raise LispError('read error: expected expression')
        token = tokens[pos]
        pos += 1
        if token.text == '(' and not token.string:
            result = []
            while pos < len(tokens) and (tokens[pos].text != ')' or tokens[pos].string):
                result.append(read())
            if pos >= len(tokens): raise LispError(f'read error at offset {token.offset}: unclosed (')
            pos += 1
            return result
        if token.text == ')' and not token.string:
            raise LispError(f'read error at offset {token.offset}: unexpected )')
        if token.text == "'" and not token.string:
            return [Symbol('quote'), read()]
        return atom(token)
    forms = []
    while pos < len(tokens): forms.append(read())
    return forms

def read_one(source):
    forms = read_all(source)
    if len(forms) != 1: raise LispError('read error: expected exactly one form')
    return forms[0]

class Env(dict):
    def __init__(self, values=None, parent=None):
        super().__init__(values or {})
        self.parent = parent
    def find(self, name):
        if name in self: return self
        if self.parent is not None: return self.parent.find(name)
        raise LispError(f'unknown symbol: {name}')
    def lookup(self, name):
        return self.find(name)[name]

@dataclass
class Builtin:
    name: str
    function: object
    minimum: int
    maximum: int | None
    def invoke(self, args):
        arity(self.name, args, self.minimum, self.maximum)
        try:
            result = self.function(*args)
            if isinstance(result, float) and not math.isfinite(result):
                raise LispError(f'{self.name}: numeric result must be finite')
            return result
        except LispError: raise
        except OverflowError:
            raise LispError(f'{self.name}: numeric overflow exceeds host range') from None
        except (TypeError, ValueError, IndexError, ZeroDivisionError) as error:
            raise LispError(f'{self.name}: {error}') from None

@dataclass
class Closure:
    parameters: list
    body: list
    environment: Env


def arity(name, args, minimum, maximum):
    if len(args) < minimum or (maximum is not None and len(args) > maximum):
        required = str(minimum) if minimum == maximum else f'{minimum}..{maximum if maximum is not None else "many"}'
        raise LispError(f'{name}: expected {required} arguments, got {len(args)}')

def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LispError('expected number (booleans are not numbers)')
    if isinstance(value, float) and not math.isfinite(value):
        raise LispError('expected finite number')
    return value

def numbers(args):
    return [number(value) for value in args]

def plus(*args): return sum(numbers(args))
def multiply(*args):
    result = 1
    for value in numbers(args): result *= value
    return result

def minus(first, *rest):
    values = numbers((first,) + rest)
    if len(values) == 1: return -values[0]
    result = values[0]
    for value in values[1:]: result -= value
    return result
def divide(first, *rest):
    values = numbers((first,) + rest)
    result = values[0] if rest else 1
    for value in values[1:] if rest else values:
        if value == 0: raise LispError('division by zero')
        result /= value
    return result

def list_value(value):
    if not isinstance(value, list): raise LispError('expected list')
    return value

def string_value(value):
    if type(value) is not str: raise LispError('expected string')
    return value

def car(value):
    value = list_value(value)
    if not value: raise LispError('car: empty list')
    return value[0]

def cdr(value):
    value = list_value(value)
    if not value: raise LispError('cdr: empty list')
    return value[1:]

def set_car(value, item):
    value = list_value(value)
    if not value: raise LispError('set-car!: empty list')
    value[0] = item
    return item

def equal(a, b):
    if isinstance(a, list) or isinstance(b, list):
        return isinstance(a,list) and isinstance(b,list) and len(a) == len(b) and all(equal(x,y) for x,y in zip(a,b))
    if isinstance(a, bool) != isinstance(b, bool): return False
    if isinstance(a, Symbol) != isinstance(b, Symbol): return False
    return a == b

def format_value(value):
    if value is True: return '#t'
    if value is False: return '#f'
    if isinstance(value, Symbol): return str(value)
    if type(value) is str:
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r') + '"'
    if isinstance(value, list):
        if len(value) == 4 and isinstance(value[0], Symbol) and value[0] == 'closure' and all(isinstance(x,list) for x in value[1:]): return '<meta-closure>'
        return '(' + ' '.join(format_value(x) for x in value) + ')'
    if isinstance(value, Closure): return '<closure>'
    if isinstance(value, Builtin): return f'<primitive:{value.name}>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number(value)
        try:
            return str(int(value)) if isinstance(value,float) and value.is_integer() else str(value)
        except (ValueError, OverflowError):
            raise LispError('print error: number exceeds host conversion limit') from None
    return str(value)

class Interpreter:
    def __init__(self, trace=False, stdin=None, stdout=None, stderr=None):
        self.trace = trace
        self.stdin, self.stdout, self.stderr = stdin or sys.stdin, stdout or sys.stdout, stderr or sys.stderr
        self.environment = Env()
        self.meta_environment = None
        self._builtins()
    def add_builtin(self, name, function, minimum, maximum=None):
        self.environment[Symbol(name)] = Builtin(name, function, minimum, maximum)
    def _builtins(self):
        for name, function, minimum in [('+', plus, 0), ('-', minus, 1), ('*', multiply, 0), ('/', divide, 1)]:
            self.add_builtin(name, function, minimum)
        if STAGE >= 10:
            for name, function in [('=', lambda a,b: number(a) == number(b)), ('<', lambda a,b: number(a) < number(b)), ('>', lambda a,b: number(a) > number(b))]:
                self.add_builtin(name, function, 2, 2)
            self.add_builtin('not', lambda x: x is False, 1, 1)
        if STAGE >= 11:
            specs = [('list', lambda *xs: list(xs), 0, None), ('cons', lambda x,xs: [x] + list_value(xs), 2, 2),
                ('car', car, 1, 1), ('cdr', cdr, 1, 1), ('null?', lambda x: isinstance(x,list) and not x, 1, 1),
                ('list?', lambda x: isinstance(x,list), 1, 1), ('symbol?', lambda x: isinstance(x,Symbol), 1, 1),
                ('number?', lambda x: not isinstance(x,bool) and isinstance(x,(int,float)), 1, 1),
                ('string?', lambda x: type(x) is str, 1, 1), ('boolean?', lambda x: isinstance(x,bool), 1, 1),
                ('equal?', equal, 2, 2), ('length', lambda x: len(list_value(x)), 1, 1),
                ('append', lambda a,b: list_value(a) + list_value(b), 2, 2), ('set-car!', set_car, 2, 2),
                ('string-append', lambda *xs: ''.join(string_value(x) for x in xs), 0, None),
                ('symbol->string', lambda x: str(x) if isinstance(x,Symbol) else self.error('expected symbol'), 1, 1),
                ('display', self.display, 1, 1), ('newline', self.newline, 0, 0),
                ('read-line', self.read_line, 0, 0), ('read', read_one, 1, 1), ('read-all', read_all, 1, 1),
                ('apply', self.apply_builtin, 2, 2), ('error', self.error, 1, 1)]
            for spec in specs: self.add_builtin(*spec)
        if STAGE >= 12:
            self.add_builtin('primitive', self.primitive, 1, 1)
            self.add_builtin('trace-event', self.trace_event, 3, 3)
            self.add_builtin('guard', self.guard, 1, 1)
    def display(self, value):
        print(value if type(value) is str else format_value(value), end='', file=self.stdout)
        return value
    def newline(self):
        print(file=self.stdout)
        return []
    def read_line(self):
        line = self.stdin.readline()
        return False if line == '' else line.rstrip('\n')
    def primitive(self, name):
        if not isinstance(name, Symbol): raise LispError('primitive: expected symbol')
        value = self.environment.lookup(name)
        if not isinstance(value, Builtin): raise LispError(f'primitive: {name} is not a primitive')
        return value
    def trace_event(self, layer, depth, expression):
        if self.trace:
            print(f'[{layer} depth={depth}] {format_value(expression)[:180]}', file=self.stderr)
        return []
    def error(self, message): raise LispError(str(message))
    def guard(self, function):
        # Recover only language errors; do not hide bugs in host Python code.
        try: return [True, self.call(function, [], 0)]
        except (LispError, RecursionError) as error: return [False, str(error)]
    def apply_builtin(self, function, args):
        return self.call(function, list_value(args), 0)
    def call(self, function, args, depth):
        if isinstance(function, Builtin): return function.invoke(args)
        if isinstance(function, Closure):
            arity('lambda', args, len(function.parameters), len(function.parameters))
            local = Env(dict(zip(function.parameters, args)), function.environment)
            return self.sequence(function.body, local, depth + 1)
        raise LispError('attempt to call a non-function')
    def sequence(self, forms, env, depth):
        result = []
        for form in forms: result = self.evaluate(form, env, depth)
        return result
    def evaluate(self, expression, env=None, depth=0):
        env = self.environment if env is None else env
        if self.trace and depth < 3:
            self.trace_event('host', depth, expression)
        if isinstance(expression, Symbol): return env.lookup(expression)
        if not isinstance(expression, list):
            if STAGE == 9 and (isinstance(expression,bool) or type(expression) is str):
                raise LispError('stage 09 supports numbers only')
            if STAGE == 10 and type(expression) is str:
                raise LispError('strings are introduced in stage 11')
            return expression
        if not expression: raise LispError('cannot evaluate empty application; use quote')
        head, args = expression[0], expression[1:]
        if STAGE >= 10 and isinstance(head, Symbol):
            if head == 'quote':
                arity('quote', args, 1, 1)
                return args[0]
            if head == 'if':
                arity('if', args, 3, 3)
                branch = args[2] if self.evaluate(args[0], env, depth + 1) is False else args[1]
                return self.evaluate(branch, env, depth + 1)
            if head == 'define':
                arity('define', args, 2, 2)
                if not isinstance(args[0], Symbol): raise LispError('define: expected symbol')
                env[args[0]] = self.evaluate(args[1], env, depth + 1)
                return args[0]
            if head == 'lambda':
                arity('lambda', args, 2, None)
                params = args[0]
                if not isinstance(params,list) or not all(isinstance(x,Symbol) for x in params):
                    raise LispError('lambda: expected list of symbols')
                if len(set(params)) != len(params): raise LispError('lambda: duplicate parameter')
                return Closure(params, args[1:], env)
            if head == 'begin': return self.sequence(args, env, depth + 1)
            if head == 'while' and STAGE >= 11:
                arity('while', args, 2, None)
                result = []
                while self.evaluate(args[0], env, depth + 1) is not False:
                    result = self.sequence(args[1:], env, depth + 1)
                return result
            if head == 'set!' and STAGE >= 11:
                arity('set!', args, 2, 2)
                if not isinstance(args[0],Symbol): raise LispError('set!: expected symbol')
                env.find(args[0])[args[0]] = self.evaluate(args[1], env, depth + 1)
                return args[0]
        function = self.evaluate(head, env, depth + 1)
        values = [self.evaluate(x, env, depth + 1) for x in args]
        return self.call(function, values, depth)
    def execute(self, source):
        forms = read_all(source)
        if STAGE < 11 and len(forms) != 1: raise LispError('before stage 11, execute exactly one form')
        return self.sequence(forms, self.environment, 0)
    def load_meta(self, path=None):
        path = Path(path) if path else Path(__file__).with_name('evaluator.lisp')
        saved_trace, self.trace = self.trace, False
        try:
            self.execute(path.read_text(encoding='utf-8'))
            self.meta_environment = self.call(self.environment.lookup(Symbol('m-global')), [], 0)
        finally:
            self.trace = saved_trace
    def meta_evaluate(self, source):
        if self.meta_environment is None: self.load_meta()
        result = []
        for form in read_all(source):
            result = self.call(self.environment.lookup(Symbol('m-eval')), [form, self.meta_environment, 0], 0)
        return result

def repl(interpreter, meta=False):
    # One form (or stage 11+ multiple forms) per line; deliberately no multiline editor.
    while True:
        if interpreter.stdin.isatty(): print('meta> ' if meta else 'lisp> ', end='', flush=True, file=interpreter.stdout)
        line = interpreter.stdin.readline()
        if line == '' or line.strip() == ':quit': return 0
        if not line.strip() or line.lstrip().startswith(';'): continue
        try:
            result = interpreter.meta_evaluate(line) if meta else interpreter.execute(line)
            print(format_value(result), file=interpreter.stdout)
        except (LispError, RecursionError) as error:
            print(f'error: {error}', file=interpreter.stderr)

def main(argv=None, interpreter=None):
    parser = argparse.ArgumentParser(description=f'Teaching Lisp stage {STAGE:02}')
    parser.add_argument('--eval', metavar='FORM')
    if STAGE >= 11: parser.add_argument('script', nargs='?', type=Path)
    if STAGE >= 12: parser.add_argument('--meta', action='store_true', help='evaluate using evaluator.lisp')
    if STAGE >= 13: parser.add_argument('--trace', action='store_true')
    if STAGE >= 14: parser.add_argument('--selfhost-repl', action='store_true', help='run Lisp-written REPL on Python host')
    args = parser.parse_args(argv)
    machine = interpreter or Interpreter(trace=getattr(args,'trace',False))
    try:
        if args.eval is not None and getattr(args,'script',None): parser.error('choose --eval or script')
        if getattr(args,'selfhost_repl',False):
            if args.eval is not None or args.script: parser.error('--selfhost-repl takes no source argument')
            machine.load_meta()
            machine.execute(Path(__file__).with_name('repl.lisp').read_text(encoding='utf-8'))
            machine.call(machine.environment.lookup(Symbol('m-repl')), [machine.meta_environment], 0)
            return 0
        source = args.eval
        if getattr(args,'script',None): source = args.script.read_text(encoding='utf-8')
        if source is None: return repl(machine, getattr(args,'meta',False))
        result = machine.meta_evaluate(source) if getattr(args,'meta',False) else machine.execute(source)
        print(format_value(result), file=machine.stdout)
        return 0
    except (LispError, RecursionError, OSError, UnicodeError) as error:
        print(f'error: {error}', file=machine.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
