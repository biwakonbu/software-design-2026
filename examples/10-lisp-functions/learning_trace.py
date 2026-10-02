"""理解確認用。既存の完成hostを観察し、評価器や提出課題を追加しない。"""

import argparse

from lisp import Closure, Interpreter, Symbol, format_value


class ObservingInterpreter(Interpreter):
    """評価をsuperへ任せ、実際の呼び出し環境と戻り値を記録する。"""

    def __init__(self):
        super().__init__()
        self.events = []
        self.active_calls = []
        self.function_names = {}

    def call(self, function, args, depth):
        if not isinstance(function, Closure):
            return super().call(function, args, depth)
        event = {"kind": "call", "name": self.function_names.get(id(function), "lambda"),
                 "captured": function.environment}
        self.events.append(event)
        self.active_calls.append(event)
        try:
            value = super().call(function, args, depth)
        finally:
            self.active_calls.pop()
        self.events.append({"kind": "return", "name": event["name"],
                            "local": event["local"], "value": value})
        return value

    def sequence(self, forms, env, depth):
        if self.active_calls and "local" not in self.active_calls[-1]:
            self.active_calls[-1]["local"] = env
        return super().sequence(forms, env, depth)

    def name_function(self, name):
        function = self.environment.lookup(Symbol(name))
        self.function_names[id(function)] = name
        return function


def closure_checkpoint():
    machine = ObservingInterpreter()
    machine.execute("(define make-adder (lambda (x) (lambda (y) (+ x y))))")
    maker = machine.name_function("make-adder")
    machine.execute("(define add5 (make-adder 5))")
    adder = machine.name_function("add5")
    saved = adder.environment
    value = machine.execute("(add5 3)")
    calls = [event for event in machine.events if event["kind"] == "call"]
    return machine, {"maker": maker, "adder": adder, "saved": saved,
                     "outer_call": calls[0], "inner_call": calls[1], "value": value}


def fact_checkpoint():
    machine = ObservingInterpreter()
    machine.execute("(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))")
    machine.name_function("fact")
    value = machine.execute("(fact 2)")
    return machine, value


def show_closure():
    machine, state = closure_checkpoint()
    saved, local = state["saved"], state["inner_call"]["local"]
    print("define make-adder: captured=G")
    print(f"call make-adder(5): E5 x={saved.lookup(Symbol('x'))}, parent=G")
    print("returned add5: captured=E5; make-adder call finished")
    print(f"call add5(3): E3 y={local.lookup(Symbol('y'))}, parent=E5")
    print(f"lookup x: E5={local.lookup(Symbol('x'))}; lookup y: E3={local.lookup(Symbol('y'))}")
    print(f"result: {format_value(state['value'])}")


def show_fact():
    machine, value = fact_checkpoint()
    for event in machine.events:
        n = event["local"].lookup(Symbol("n"))
        if event["kind"] == "call":
            print(f"call fact: n={n}")
        else:
            print(f"return fact: n={n} => {format_value(event['value'])}")
    print(f"result: {format_value(value)}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="完成hostの環境寿命と再帰を観察する補足")
    parser.add_argument("case", nargs="?", default="all", choices=("closure", "fact", "all"))
    args = parser.parse_args(argv)
    for name, show in (("closure", show_closure), ("fact", show_fact)):
        if args.case in (name, "all"):
            print(f"[{name}]")
            show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
