"""Runnable exercise starter: extend square to reject negative inputs."""
from lisp import Interpreter, main, number
machine = Interpreter()
machine.add_builtin('square', lambda x: number(x) ** 2, 1, 1)
if __name__ == '__main__':
    raise SystemExit(main(interpreter=machine))
