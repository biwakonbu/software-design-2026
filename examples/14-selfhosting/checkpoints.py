"""理解確認用。完成したLisp製評価器を段階ごとに使う観察driver。"""

import argparse
import io

from lisp import Interpreter, Symbol, format_value, main as lisp_main, read_one


def ready_machine():
    machine = Interpreter()
    machine.load_meta()
    return machine


def helper(machine, name, *values):
    """host上で動く既存のLisp関数を呼ぶ。対象式をPythonで評価しない。"""
    return machine.call(machine.environment.lookup(Symbol(name)), list(values), 0)


def minimal_checkpoint():
    machine = ready_machine()
    sources = ("42", "(quote (+ 2 3))", "(+ 1 (* 2 3))", "(if #f (/ 1 0) 9)")
    return [(source, machine.meta_evaluate(source)) for source in sources]


def environment_checkpoint():
    machine = ready_machine()
    machine.meta_evaluate("(define x 5)")
    global_env = machine.meta_environment
    child = helper(machine, "m-new-env", global_env)
    helper(machine, "m-define", Symbol("y"), 3, child)
    return machine, global_env, child


def closure_checkpoint():
    machine = ready_machine()
    machine.meta_evaluate("(define square (lambda (x) (* x x)))")
    global_env = machine.meta_environment
    closure = helper(machine, "m-lookup", Symbol("square"), global_env)
    form = read_one("(square 6)")
    values = helper(machine, "m-eval-list", form[1:], global_env, 0)
    # 観察用E6を作る。通常のm-applyも、この3つの既存関数を使う。
    child = helper(machine, "m-new-env", closure[3])
    helper(machine, "m-bind", closure[1], values, child)
    body_value = helper(machine, "m-sequence", closure[2], child, 0)
    normal_value = machine.meta_evaluate("(square 6)")
    return machine, {"global": global_env, "closure": closure, "arguments": values,
                     "child": child, "body_value": body_value, "normal_value": normal_value}


REPL_INPUT = (
    "(define square (lambda (x) (* x x)))\n"
    "(square 6)\n"
    "(/ 1 0)\n"
    "(square 7)\n"
    "primitive\n"
    "(square 3)\n"
    ":quit\n"
)


def repl_checkpoint(source=REPL_INPUT):
    stdout, stderr = io.StringIO(), io.StringIO()
    machine = Interpreter(stdin=io.StringIO(source), stdout=stdout, stderr=stderr)
    status = lisp_main(["--selfhost-repl"], machine)
    return status, stdout.getvalue(), stderr.getvalue()


def show_minimal():
    for source, value in minimal_checkpoint():
        print(f"meta {source} => {format_value(value)}")


def show_environment():
    machine, global_env, child = environment_checkpoint()
    print(f"G: x={helper(machine, 'm-lookup', Symbol('x'), global_env)}")
    print(f"E3: y={helper(machine, 'm-lookup', Symbol('y'), child)}, parent=G")
    print(f"lookup x in E3 => {helper(machine, 'm-lookup', Symbol('x'), child)}")
    print(f"lookup y in E3 => {helper(machine, 'm-lookup', Symbol('y'), child)}")


def show_closure():
    machine, state = closure_checkpoint()
    print(f"square: params={format_value(state['closure'][1])}, captured=G")
    print(f"argument values: {format_value(state['arguments'])}")
    print(f"observation E6: x={helper(machine, 'm-lookup', Symbol('x'), state['child'])}, parent=G")
    print(f"lookup * in E6 => {format_value(helper(machine, 'm-lookup', Symbol('*'), state['child']))}")
    print(f"body (* x x) => {format_value(state['body_value'])}")
    print(f"normal (square 6) => {format_value(state['normal_value'])}")


def show_repl():
    status, output, errors = repl_checkpoint()
    print(output, end="")
    if status != 0 or errors:
        raise RuntimeError(f"REPL checkpoint failed: status={status}, stderr={errors}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="完成metaの段階を観察する補足。提出課題ではありません")
    parser.add_argument("case", nargs="?", default="all",
                        choices=("minimal", "environment", "closure", "repl", "all"))
    args = parser.parse_args(argv)
    for name, show in (("minimal", show_minimal), ("environment", show_environment),
                       ("closure", show_closure), ("repl", show_repl)):
        if args.case in (name, "all"):
            print(f"[{name}]")
            show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
