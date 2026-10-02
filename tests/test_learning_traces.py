"""補足例の理解確認。既存の学生課題・fixture・採点契約は変更しない。"""

import importlib.util
import re
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_supplement(stage, filename):
    folder = ROOT / "examples" / stage
    core = load(f"learning_core_{stage[:2]}", folder / "lisp.py")
    previous = sys.modules.get("lisp")
    sys.modules["lisp"] = core
    try:
        supplement = load(f"learning_supplement_{stage[:2]}", folder / filename)
    finally:
        if previous is None:
            del sys.modules["lisp"]
        else:
            sys.modules["lisp"] = previous
    return core, supplement


HOST, TRACE = load_supplement("10-lisp-functions", "learning_trace.py")
META, CHECK = load_supplement("14-selfhosting", "checkpoints.py")


class ClosureLifetimeTests(unittest.TestCase):
    def test_creator_call_ends_but_environment_remains(self):
        machine, state = TRACE.closure_checkpoint()
        self.assertEqual(state["value"], 8)
        self.assertEqual(machine.active_calls, [])
        self.assertIs(state["maker"].environment, machine.environment)
        self.assertIs(state["saved"], state["outer_call"]["local"])
        self.assertIs(state["inner_call"]["local"].parent, state["saved"])
        self.assertEqual(state["saved"].lookup(HOST.Symbol("x")), 5)
        self.assertNotIn(HOST.Symbol("x"), machine.environment)
        self.assertNotIn(HOST.Symbol("y"), state["saved"])

    def test_callers_x_does_not_replace_captured_x(self):
        machine, _ = TRACE.closure_checkpoint()
        self.assertEqual(machine.execute("((lambda (x) (add5 3)) 100)"), 8)

    def test_separate_returned_functions_keep_separate_inputs(self):
        machine, state = TRACE.closure_checkpoint()
        machine.execute("(define add10 (make-adder 10))")
        second = machine.environment.lookup(HOST.Symbol("add10"))
        self.assertIsNot(second.environment, state["saved"])
        self.assertEqual(machine.execute("(add10 3)"), 13)
        self.assertEqual(machine.execute("(add5 3)"), 8)

    def test_recursion_records_descent_and_actual_return_values(self):
        machine, value = TRACE.fact_checkpoint()
        calls = [e for e in machine.events if e["kind"] == "call"]
        returns = [e for e in machine.events if e["kind"] == "return"]
        self.assertEqual([e["local"][HOST.Symbol("n")] for e in calls], [2, 1, 0])
        self.assertEqual([e["value"] for e in returns], [1, 1, 2])
        self.assertEqual(len({id(e["local"]) for e in calls}), 3)
        self.assertTrue(all(e["local"].parent is machine.environment for e in calls))
        self.assertEqual(value, 2)
        self.assertNotIn(HOST.Symbol("n"), machine.environment)


class MetaCheckpointTests(unittest.TestCase):
    def test_minimal_quote_stays_data_and_if_skips_failure(self):
        results = CHECK.minimal_checkpoint()
        self.assertEqual([META.format_value(value) for _, value in results],
                         ["42", "(+ 2 3)", "7", "9"])
        self.assertIsInstance(results[1][1][0], META.Symbol)

    def test_child_lookup_uses_parent_and_own_frame(self):
        machine, global_env, child = CHECK.environment_checkpoint()
        self.assertIs(child[1], global_env)
        self.assertEqual(CHECK.helper(machine, "m-lookup", META.Symbol("x"), child), 5)
        self.assertEqual(CHECK.helper(machine, "m-lookup", META.Symbol("y"), child), 3)
        with self.assertRaisesRegex(META.LispError, "unknown symbol: y"):
            CHECK.helper(machine, "m-lookup", META.Symbol("y"), global_env)

    def test_shadowing_keeps_parent_input(self):
        machine, global_env, child = CHECK.environment_checkpoint()
        CHECK.helper(machine, "m-define", META.Symbol("x"), 20, child)
        self.assertEqual(CHECK.helper(machine, "m-lookup", META.Symbol("x"), child), 20)
        self.assertEqual(CHECK.helper(machine, "m-lookup", META.Symbol("x"), global_env), 5)

    def test_shared_frame_updates_are_visible_from_child(self):
        machine, global_env, child = CHECK.environment_checkpoint()
        CHECK.helper(machine, "m-define", META.Symbol("x"), 7, global_env)
        self.assertEqual(CHECK.helper(machine, "m-lookup", META.Symbol("x"), child), 7)

    def test_square_steps_and_normal_application_agree(self):
        machine, state = CHECK.closure_checkpoint()
        self.assertIs(state["closure"][3], state["global"])
        self.assertIs(state["child"][1], state["global"])
        self.assertEqual(state["arguments"], [6])
        self.assertEqual(CHECK.helper(machine, "m-lookup", META.Symbol("x"), state["child"]), 6)
        self.assertEqual(state["body_value"], 36)
        self.assertEqual(state["normal_value"], 36)
        with self.assertRaisesRegex(META.LispError, "unknown symbol: x"):
            machine.meta_evaluate("x")

    def test_meta_closure_keeps_live_definition_environment(self):
        machine = CHECK.ready_machine()
        machine.meta_evaluate("(define factor 2) (define scaled (lambda (x) (* factor x)))")
        self.assertEqual(machine.meta_evaluate("(scaled 6)"), 12)
        machine.meta_evaluate("(set! factor 3)")
        self.assertEqual(machine.meta_evaluate("((lambda (factor) (scaled 6)) 100)"), 18)

    def test_repl_preserves_definition_after_errors_and_hides_host_api(self):
        status, output, errors = CHECK.repl_checkpoint()
        self.assertEqual(status, 0)
        self.assertEqual(errors, "")
        self.assertEqual(output, "square\n36\nerror: division by zero\n49\n"
                                 "error: unknown symbol: primitive\n9\n")

    def test_repl_recovers_read_error_without_losing_definition(self):
        status, output, errors = CHECK.repl_checkpoint("(define n 6)\n(\n(+ n 1)\n:quit\n")
        self.assertEqual(status, 0)
        self.assertEqual(errors, "")
        self.assertEqual(output.splitlines()[0], "n")
        self.assertTrue(output.splitlines()[1].startswith("error: "))
        self.assertEqual(output.splitlines()[-1], "7")

    def test_protected_helpers_are_not_target_names(self):
        machine = CHECK.ready_machine()
        for name in ("primitive", "guard", "trace-event", "m-eval"):
            with self.subTest(name=name), self.assertRaisesRegex(META.LispError, "unknown symbol"):
                machine.meta_evaluate(name)


class SupplementCLITests(unittest.TestCase):
    def test_each_case_matches_independent_readme_output(self):
        for folder, filename, cases in (
            ("10-lisp-functions", "learning_trace.py", ("closure", "fact")),
            ("14-selfhosting", "checkpoints.py", ("minimal", "environment", "closure", "repl")),
        ):
            readme = (ROOT / "examples" / folder / "README.md").read_text(encoding="utf-8")
            for case in cases:
                with self.subTest(folder=folder, case=case):
                    expected = re.search(rf"{case}の期待出力：\n\n```text\n(.*?)```", readme, re.S)[1]
                    result = subprocess.run([sys.executable, str(ROOT / "examples" / folder / filename), case],
                                            cwd=ROOT, text=True, capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    self.assertEqual(result.stdout, expected)

    def test_default_runs_all_and_unknown_case_is_usage_error(self):
        for folder, filename, count in (("10-lisp-functions", "learning_trace.py", 2),
                                        ("14-selfhosting", "checkpoints.py", 4)):
            script = ROOT / "examples" / folder / filename
            result = subprocess.run([sys.executable, str(script)], text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(re.findall(r"(?m)^\[\w+\]$", result.stdout)), count)
            result = subprocess.run([sys.executable, str(script), "unknown"], text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
