"""Meaningful language semantics, stage boundaries, and CLI regression tests."""
from pathlib import Path
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = {
    9: '09-lisp-arithmetic', 10: '10-lisp-functions', 11: '11-lisp-scripts',
    12: '12-meta-evaluator', 13: '13-language-review', 14: '14-selfhosting', 15: '15-showcase',
}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclass annotations resolve the module here
    spec.loader.exec_module(module)
    return module


CALC = load('teaching_calculator', ROOT / 'examples/08-calculator/calculator.py')
MODULES = {stage: load(f'teaching_lisp_{stage}', ROOT / 'examples' / folder / 'lisp.py')
           for stage, folder in FOLDERS.items()}
LISP = MODULES[14]


def cli(stage, *args, input_text=None, env=None):
    return subprocess.run([sys.executable, str(ROOT / 'examples' / FOLDERS[stage] / 'lisp.py'), *args],
                          input=input_text, text=True, capture_output=True, timeout=15, env=env)


class CalculatorTests(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(CALC.calculate('1 + 2'), 3)

    def test_precedence(self):
        self.assertEqual(CALC.calculate('2 + 3 * 4'), 14)

    def test_parentheses(self):
        self.assertEqual(CALC.calculate('(2 + 3) * 4'), 20)

    def test_left_associative_subtraction(self):
        self.assertEqual(CALC.calculate('10 - 3 - 2'), 5)

    def test_left_associative_division(self):
        self.assertEqual(CALC.calculate('20 / 2 / 5'), 2)

    def test_unary(self):
        self.assertEqual(CALC.calculate('-(-2) + +3'), 5)

    def test_decimal_without_leading_digit(self):
        self.assertAlmostEqual(CALC.calculate('.5 + 1.25'), 1.75)

    def test_zero(self):
        self.assertEqual(CALC.calculate('0 * 100'), 0)

    def test_ast_structure(self):
        node = CALC.parse('2 + 3 * 4')
        self.assertIsInstance(node, CALC.Binary)
        self.assertEqual(node.op, '+')
        self.assertEqual(node.right.op, '*')

    def test_token_offsets(self):
        tokens = CALC.tokenize(' 12 + 3')
        self.assertEqual([(t.kind, t.offset) for t in tokens], [('number', 1), ('+', 4), ('number', 6), ('eof', 7)])

    def test_lexical_error(self):
        with self.assertRaisesRegex(CALC.CalculatorError, 'lexical'):
            CALC.calculate('1 + x')

    def test_non_ascii_digits_are_lexical_errors(self):
        for source in ['٢+٣','２+３','१२+३']:
            with self.subTest(source=source), self.assertRaisesRegex(CALC.CalculatorError,'lexical'):
                CALC.calculate(source)

    def test_missing_parenthesis(self):
        with self.assertRaisesRegex(CALC.CalculatorError, 'expected'):
            CALC.calculate('(1 + 2')

    def test_extra_token(self):
        with self.assertRaisesRegex(CALC.CalculatorError, 'unexpected'):
            CALC.calculate('1 2')

    def test_empty_source(self):
        with self.assertRaises(CALC.CalculatorError):
            CALC.calculate('')

    def test_operator_without_operand(self):
        with self.assertRaises(CALC.CalculatorError):
            CALC.calculate('2 +')

    def test_division_by_zero_semantic(self):
        node = CALC.parse('1 / (2 - 2)')
        with self.assertRaisesRegex(CALC.CalculatorError, 'semantic'):
            CALC.evaluate(node)

    def test_python_code_rejected(self):
        with self.assertRaises(CALC.CalculatorError):
            CALC.calculate("__import__('os')")

    def test_unknown_ast_operator_rejected(self):
        for node in [CALC.Unary('?',CALC.Number(1)),CALC.Binary('?',CALC.Number(1),CALC.Number(2))]:
            with self.subTest(node=node), self.assertRaisesRegex(CALC.CalculatorError,'unknown'):
                CALC.evaluate(node)

    def test_unknown_ast_rejected(self):
        with self.assertRaisesRegex(CALC.CalculatorError, 'unknown AST'):
            CALC.evaluate(object())


class ReaderTests(unittest.TestCase):
    def test_nested_ast(self):
        self.assertEqual(LISP.read_one('(+ 1 (* 2 3))'), [LISP.Symbol('+'), 1, [LISP.Symbol('*'), 2, 3]])

    def test_comment(self):
        self.assertEqual(LISP.read_all('; first\n(+ 1 2) ; end\n4'), [[LISP.Symbol('+'), 1, 2], 4])

    def test_quote_empty(self):
        self.assertEqual(LISP.read_one("'()"), [LISP.Symbol('quote'), []])

    def test_quoted_symbol_type(self):
        self.assertIsInstance(LISP.read_one("'name")[1], LISP.Symbol)

    def test_string_parentheses_are_data(self):
        self.assertEqual(LISP.read_one('"a (b); c"'), 'a (b); c')

    def test_string_escapes(self):
        self.assertEqual(LISP.read_one(r'"a\nb\t\"c\\d"'), 'a\nb\t"c\\d')

    def test_utf8(self):
        self.assertEqual(LISP.read_one('"日本語"'), '日本語')

    def test_negative_and_exponent_numbers(self):
        self.assertEqual(LISP.read_all('-12 1.5 1e2'), [-12, 1.5, 100.0])

    def test_extra_close(self):
        with self.assertRaisesRegex(LISP.LispError, 'unexpected'):
            LISP.read_all('(+ 1 2))')

    def test_unclosed_list(self):
        with self.assertRaisesRegex(LISP.LispError, 'unclosed'):
            LISP.read_all('(+ 1')

    def test_unclosed_string(self):
        with self.assertRaisesRegex(LISP.LispError, 'unclosed string'):
            LISP.read_all('"oops')

    def test_unrecognized_escape(self):
        with self.assertRaisesRegex(LISP.LispError, 'unknown escape'):
            LISP.read_all(r'"\q"')

    def test_read_one_rejects_multiple(self):
        with self.assertRaisesRegex(LISP.LispError, 'exactly one'):
            LISP.read_one('1 2')

    def test_quote_needs_expression(self):
        with self.assertRaisesRegex(LISP.LispError, 'expected expression'):
            LISP.read_one("'")

    def test_symbol_and_string_format_roundtrip(self):
        value = [LISP.Symbol('x'), '日本語\n"z"', True, []]
        self.assertEqual(LISP.read_one(LISP.format_value(value)), value)
        self.assertIsInstance(LISP.read_one(LISP.format_value(value))[0], LISP.Symbol)


class HostSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.machine = LISP.Interpreter(stdin=io.StringIO(), stdout=io.StringIO(), stderr=io.StringIO())

    def value(self, source):
        return self.machine.execute(source)

    def test_variadic_arithmetic(self):
        self.assertEqual(self.value('(+ 10 2 (* 2 4))'), 20)
        self.assertEqual(self.value('(- 20 3 4)'), 13)

    def test_zero_arity_identities(self):
        self.assertEqual(self.value('(+ )'), 0)
        self.assertEqual(self.value('(*)'), 1)

    def test_unary_arithmetic(self):
        self.assertEqual(self.value('(- 5)'), -5)
        self.assertEqual(self.value('(/ 4)'), .25)

    def test_division_zero(self):
        with self.assertRaisesRegex(LISP.LispError, 'division by zero'):
            self.value('(/ 10 0)')

    def test_boolean_not_number(self):
        with self.assertRaisesRegex(LISP.LispError, 'number'):
            self.value('(+ #t 1)')

    def test_primitive_arity(self):
        with self.assertRaisesRegex(LISP.LispError, 'arguments'):
            self.value('(-)')
        with self.assertRaisesRegex(LISP.LispError, 'arguments'):
            self.value('(= 1 2 3)')

    def test_unknown_symbol(self):
        with self.assertRaisesRegex(LISP.LispError, 'unknown symbol'):
            self.value('missing')

    def test_define_persists(self):
        self.value('(define x 10)')
        self.assertEqual(self.value('(+ x 2)'), 12)

    def test_if_short_circuit(self):
        self.assertEqual(self.value('(if #f (/ 1 0) 42)'), 42)

    def test_truth_only_false_is_false(self):
        self.assertEqual(self.value('(if 0 1 2)'), 1)
        self.assertEqual(self.value("(if '() 1 2)"), 1)
        self.assertTrue(self.value('(not #f)'))
        self.assertFalse(self.value('(not 0)'))

    def test_quote_symbol(self):
        self.assertEqual(self.value("'missing"), LISP.Symbol('missing'))

    def test_empty_quote_vs_application(self):
        self.assertEqual(self.value("'()"), [])
        with self.assertRaisesRegex(LISP.LispError, 'empty application'):
            self.value('()')

    def test_lambda(self):
        self.assertEqual(self.value('((lambda (x y) (+ x y)) 2 3)'), 5)

    def test_lambda_arity(self):
        with self.assertRaisesRegex(LISP.LispError, 'arguments'):
            self.value('((lambda (x) x) 1 2)')

    def test_bad_lambda_parameters(self):
        with self.assertRaisesRegex(LISP.LispError, 'symbols'):
            self.value('(lambda (1) 1)')
        with self.assertRaisesRegex(LISP.LispError, 'duplicate'):
            self.value('(lambda (x x) x)')

    def test_lambda_needs_body(self):
        with self.assertRaisesRegex(LISP.LispError, 'arguments'):
            self.value('(lambda (x))')

    def test_special_form_arity(self):
        for source in ['(if #t 1)', '(quote 1 2)', '(define x)', '(set! x)']:
            with self.subTest(source=source), self.assertRaisesRegex(LISP.LispError, 'arguments'):
                self.value(source)

    def test_invalid_define_target(self):
        with self.assertRaisesRegex(LISP.LispError, 'expected symbol'):
            self.value('(define 1 2)')

    def test_non_function_call(self):
        with self.assertRaisesRegex(LISP.LispError, 'non-function'):
            self.value('(1 2)')

    def test_lexical_scope(self):
        self.assertEqual(self.value('(begin (define x 10) (define f (lambda (y) (+ x y))) ((lambda (x) (f 1)) 99))'), 11)

    def test_closure_survives_creator(self):
        self.assertEqual(self.value('(begin (define make (lambda (x) (lambda (y) (+ x y)))) (define add (make 10)) (add 3))'), 13)

    def test_local_binding_does_not_leak(self):
        self.value('((lambda () (define local 2) local))')
        with self.assertRaisesRegex(LISP.LispError, 'unknown symbol'):
            self.value('local')

    def test_recursion(self):
        self.assertEqual(self.value('(begin (define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1)))))) (fact 6))'), 720)

    def test_closure_observes_environment_update(self):
        self.assertEqual(self.value('(begin (define x 1) (define f (lambda () x)) (set! x 9) (f))'), 9)

    def test_set_nearest_scope(self):
        self.assertEqual(self.value('(begin (define x 1) ((lambda (x) (set! x 9) x) 2) x)'), 1)

    def test_set_unbound_error(self):
        with self.assertRaisesRegex(LISP.LispError, 'unknown symbol'):
            self.value('(set! absent 3)')

    def test_lists(self):
        self.assertEqual(self.value("(cons 1 '(2 3))"), [1, 2, 3])
        self.assertEqual(self.value("(car '(4 5))"), 4)
        self.assertEqual(self.value("(cdr '(4 5))"), [5])

    def test_cdr_copy_semantics(self):
        self.assertEqual(self.value("(begin (define xs '(1 2)) (define tail (cdr xs)) (set-car! tail 9) xs)"), [1, 2])

    def test_set_car_mutates(self):
        self.assertEqual(self.value("(begin (define xs '(1 2)) (set-car! xs 9) xs)"), [9, 2])

    def test_list_type_errors(self):
        for source in ['(car 1)', '(cdr 1)', '(car (list))', '(set-car! (list) 1)']:
            with self.subTest(source=source), self.assertRaises(LISP.LispError):
                self.value(source)

    def test_type_predicates(self):
        self.assertEqual(self.value("(list (null? '()) (symbol? 'x) (string? \"x\") (number? #t) (boolean? #t))"), [True, True, True, False, True])

    def test_equal_type_distinctions(self):
        self.assertEqual(self.value("(list (equal? 'x \"x\") (equal? #t 1) (equal? '(1 2) '(1 2)))"), [False, False, True])

    def test_apply_closure(self):
        self.assertEqual(self.value('(apply (lambda (x y) (+ x y)) (list 2 3))'), 5)

    def test_string_io(self):
        self.assertEqual(self.value('(string-append "日" "本")'), '日本')
        self.value('(display "hello") (newline)')
        self.assertEqual(self.machine.stdout.getvalue(), 'hello\n')

    def test_read_is_not_eval(self):
        self.assertEqual(self.value('(read "(+ 1 2)")'), [LISP.Symbol('+'), 1, 2])

    def test_read_line_eof(self):
        self.assertIs(self.value('(read-line)'), False)

    def test_multiform_script(self):
        self.assertEqual(self.value('(define x 2)\n(define y 3)\n(+ x y)'), 5)

    def test_parse_before_side_effects(self):
        with self.assertRaises(LISP.LispError):
            self.value('(define x 2) (')
        with self.assertRaises(LISP.LispError):
            self.value('x')

    def test_while(self):
        self.assertEqual(self.value('(begin (define i 3) (while (> i 0) (set! i (- i 1))) i)'), 0)
        self.assertEqual(self.value('(while #f 99)'), [])

    def test_subtraction_is_sequential_for_floats(self):
        self.assertEqual(self.value('(- 1e16 1e16 1)'), -1)

    def test_equal_nested_type_distinctions(self):
        self.assertFalse(self.value("(equal? '(#t) '(1))"))
        self.assertFalse(self.value("""(equal? '(x) '("x"))"""))

    def test_guard_error_recovery(self):
        self.assertEqual(self.value('(guard (lambda () (/ 1 0)))'), [False, 'division by zero'])


class MetaAndStageTests(unittest.TestCase):
    def test_verified_variadic_regressions(self):
        cases = [
            ('(+ 1 20 300 4000 50000)', 54321),
            ('(* 1 1 5 1 1 1 7 1 1 1 11)', 385),
            ('(- 96 20 1 1 1)', 73),
            ('(/ 10 2 2 2)', 1.25),
            ('(+ 20 5 (- 10 5 3) (* 3 4 (/ 12 3)))', 75),
        ]
        for stage, module in MODULES.items():
            for source, expected in cases:
                with self.subTest(stage=stage, source=source, layer='host'):
                    self.assertEqual(module.Interpreter().execute(source), expected)
                if stage >= 12:
                    with self.subTest(stage=stage, source=source, layer='meta'):
                        self.assertEqual(module.Interpreter().meta_evaluate(source), expected)

    def test_stage9_numbers_only(self):
        module = MODULES[9]
        for source in ['#t', '"x"', '(define x 1)', "'()"]:
            with self.subTest(source=source), self.assertRaises(module.LispError):
                module.Interpreter().execute(source)

    def test_stage10_single_form(self):
        module = MODULES[10]
        with self.assertRaisesRegex(module.LispError, 'exactly one'):
            module.Interpreter().execute('1 2')

    def test_stage10_no_string_evaluation(self):
        module = MODULES[10]
        with self.assertRaisesRegex(module.LispError, 'stage 11'):
            module.Interpreter().execute('"x"')

    def test_all_stages_arithmetic(self):
        for stage, module in MODULES.items():
            with self.subTest(stage=stage):
                self.assertEqual(module.Interpreter().execute('(+ 1 (* 2 3))'), 7)

    def test_stage12_meta_start(self):
        machine = MODULES[12].Interpreter()
        self.assertEqual(machine.meta_evaluate('(if #f (/ 1 0) (+ 2 3))'), 5)
        self.assertEqual(machine.meta_evaluate("'()"), [])

    def test_stage12_meta_boundary(self):
        module = MODULES[12]
        with self.assertRaisesRegex(module.LispError, 'stage 12 meta'):
            module.Interpreter().meta_evaluate('(define x 2)')

    def test_fixture_host_meta_all_late_stages(self):
        cases = json.loads((ROOT / 'examples/15-showcase/compatibility.json').read_text())
        for stage in (13, 14, 15):
            module = MODULES[stage]
            for case in cases:
                for meta in (False, True):
                    with self.subTest(stage=stage, source=case['source'], meta=meta):
                        machine = module.Interpreter()
                        evaluate = machine.meta_evaluate if meta else machine.execute
                        if 'expected' in case:
                            self.assertEqual(module.format_value(evaluate(case['source'])), case['expected'])
                        else:
                            with self.assertRaisesRegex(module.LispError, case['error']):
                                evaluate(case['source'])

    def test_meta_does_not_delegate_source_to_host_eval(self):
        # Replacing host + cannot alter the semantics of define or lambda in m-eval.
        machine = LISP.Interpreter()
        machine.load_meta()
        host_evaluate = machine.evaluate
        observed = []
        def record(expression, env=None, depth=0):
            if isinstance(expression, list) and expression and expression[0] == LISP.Symbol('user-f'):
                observed.append(expression)
            return host_evaluate(expression, env, depth)
        machine.evaluate = record
        self.assertEqual(machine.meta_evaluate('(begin (define user-f (lambda (x) x)) (user-f 7))'), 7)
        self.assertEqual(observed, [])

    def test_meta_environment_persists(self):
        machine = LISP.Interpreter()
        machine.meta_evaluate('(define x 7)')
        self.assertEqual(machine.meta_evaluate('(+ x 1)'), 8)

    def test_meta_local_scope_does_not_leak(self):
        machine = LISP.Interpreter()
        machine.meta_evaluate('((lambda () (define local 2) local))')
        with self.assertRaisesRegex(LISP.LispError, 'unknown symbol'):
            machine.meta_evaluate('local')

    def test_meta_bad_parameters_and_non_function(self):
        for source in ['(lambda (1) 1)', '(lambda x x)', '(lambda (x))', '(1 2)']:
            with self.subTest(source=source), self.assertRaises(LISP.LispError):
                LISP.Interpreter().meta_evaluate(source)

    def test_persistent_local_closure_mutation_both_layers(self):
        source = '(begin (define make-counter (lambda () (define n 0) (lambda () (set! n (+ n 1)) n))) (define count (make-counter)) (count) (count))'
        for meta in (False,True):
            with self.subTest(meta=meta):
                machine = LISP.Interpreter()
                self.assertEqual(machine.meta_evaluate(source) if meta else machine.execute(source),2)

    def test_invalid_target_rejects_before_side_effect_both_layers(self):
        for source in ['(define 1 (display "bad"))','(set! 1 (display "bad"))']:
            for meta in (False,True):
                with self.subTest(source=source,meta=meta):
                    output = io.StringIO()
                    machine = LISP.Interpreter(stdout=output)
                    with self.assertRaisesRegex(LISP.LispError,'expected symbol'):
                        machine.meta_evaluate(source) if meta else machine.execute(source)
                    self.assertEqual(output.getvalue(),'')

    def test_meta_two_layers_trace(self):
        errors = io.StringIO()
        machine = LISP.Interpreter(trace=True, stderr=errors)
        self.assertEqual(machine.meta_evaluate('(+ 1 2)'), 3)
        self.assertIn('[host depth=', errors.getvalue())
        self.assertIn('[meta depth=', errors.getvalue())

    def test_meta_closure_display(self):
        machine = LISP.Interpreter()
        closure = machine.meta_evaluate('(begin (define f (lambda (x) x)) f)')
        self.assertEqual(LISP.format_value(closure), '<meta-closure>')

    def test_closure_word_can_be_quoted_data(self):
        machine = LISP.Interpreter()
        self.assertEqual(LISP.format_value(machine.meta_evaluate("'(closure 1)")),'(closure 1)')

    def test_meta_empty_while(self):
        self.assertEqual(LISP.Interpreter().meta_evaluate('(while #f 7)'), [])


class NumericBoundaryTests(unittest.TestCase):
    def test_integer_to_float_overflow_all_layers(self):
        source = '(/ ' + '9' * 310 + ' 1)'
        for stage, module in MODULES.items():
            for meta in ([False,True] if stage>=12 else [False]):
                with self.subTest(stage=stage,meta=meta):
                    machine = module.Interpreter()
                    with self.assertRaisesRegex(module.LispError,'overflow'):
                        machine.meta_evaluate(source) if meta else machine.execute(source)

    def test_nonfinite_result_all_layers(self):
        for source in ['(* 1e308 2)','(+ 1e308 1e308)','(/ 1e308 1e-308)']:
            for stage,module in MODULES.items():
                for meta in ([False,True] if stage>=12 else [False]):
                    with self.subTest(source=source,stage=stage,meta=meta):
                        machine = module.Interpreter()
                        with self.assertRaisesRegex(module.LispError,'finite'):
                            machine.meta_evaluate(source) if meta else machine.execute(source)

    def test_nonfinite_literals_all_readers(self):
        for stage,module in MODULES.items():
            for source in ['1e309','-1e309','1e999999']:
                with self.subTest(stage=stage,source=source), self.assertRaisesRegex(module.LispError,'read error.*finite'):
                    module.read_one(source)

    def test_nonfinite_host_values_rejected(self):
        for stage,module in MODULES.items():
            for value in [float('inf'),float('-inf'),float('nan')]:
                with self.subTest(stage=stage,value=value):
                    with self.assertRaisesRegex(module.LispError,'finite'):
                        module.number(value)
                    with self.assertRaisesRegex(module.LispError,'finite'):
                        module.format_value(value)

    def test_integer_digit_limit_read_errors_not_symbols(self):
        previous = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(640)
            for stage,module in MODULES.items():
                with self.subTest(stage=stage), self.assertRaisesRegex(module.LispError,'read error.*conversion limit'):
                    module.read_one('9'*641)
        finally:
            sys.set_int_max_str_digits(previous)

    def test_integer_result_print_limit_is_language_error(self):
        previous = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(640)
            source='(* ' + '9'*600 + ' ' + '9'*600 + ')'
            for stage,module in MODULES.items():
                for meta in ([False,True] if stage>=12 else [False]):
                    with self.subTest(stage=stage,meta=meta):
                        machine=module.Interpreter()
                        value=machine.meta_evaluate(source) if meta else machine.execute(source)
                        with self.assertRaisesRegex(module.LispError,'print error.*conversion limit'):
                            module.format_value(value)
        finally:
            sys.set_int_max_str_digits(previous)

    def test_large_integer_ratio_can_still_be_finite(self):
        source='(/ '+'9'*310+' '+'9'*310+')'
        for stage,module in MODULES.items():
            for meta in ([False,True] if stage>=12 else [False]):
                with self.subTest(stage=stage,meta=meta):
                    machine=module.Interpreter()
                    self.assertEqual(machine.meta_evaluate(source) if meta else machine.execute(source),1)

    def test_very_small_finite_values_remain_supported(self):
        for stage,module in MODULES.items():
            with self.subTest(stage=stage):
                self.assertEqual(module.Interpreter().execute('(* 1e-308 2)'),2e-308)

    def test_numeric_repl_recovery_all_stages_and_layers(self):
        env=dict(os.environ,PYTHONINTMAXSTRDIGITS='640')
        overflow='(/ '+'9'*310+' 1)'
        unprintable='(* '+'9'*600+' '+'9'*600+')'
        source='\n'.join([overflow,'(* 1e308 2)','1e309','9'*641,unprintable,'(+ 1 2)',':quit'])+'\n'
        for stage in FOLDERS:
            modes=[()]
            if stage>=12: modes.append(('--meta',))
            if stage>=14: modes.append(('--selfhost-repl',))
            for args in modes:
                with self.subTest(stage=stage,args=args):
                    result=cli(stage,*args,input_text=source,env=env)
                    self.assertEqual(result.returncode,0)
                    self.assertTrue(result.stdout.endswith('3\n'),result.stdout[-200:])
                    errors=result.stdout if args==('--selfhost-repl',) else result.stderr
                    self.assertEqual(sum(line.startswith('error: ') for line in errors.splitlines()),5)
                    self.assertIn('overflow',errors)
                    self.assertIn('finite',errors)
                    self.assertIn('conversion limit',errors)
                    self.assertIn('print error',errors)
                    self.assertNotIn('Traceback',result.stdout+result.stderr)

    def test_numeric_error_cli_status_all_stages(self):
        source='(/ '+'9'*310+' 1)'
        for stage in FOLDERS:
            for args in ([(),('--meta',)] if stage>=12 else [()]):
                with self.subTest(stage=stage,args=args):
                    result=cli(stage,*args,'--eval',source)
                    self.assertEqual(result.returncode,1)
                    self.assertIn('overflow',result.stderr)
                    self.assertNotIn('Traceback',result.stderr)

    def test_stage_copy_consistency(self):
        sources=[]
        for folder in FOLDERS.values():
            text=(ROOT/'examples'/folder/'lisp.py').read_text()
            sources.append(LISP.re.sub(r'STAGE = \d+','STAGE = N',text))
        self.assertEqual(len(set(sources)),1)


class CliTests(unittest.TestCase):
    def test_all_stage_eval_cli(self):
        for stage in FOLDERS:
            with self.subTest(stage=stage):
                result = cli(stage, '--eval', '(+ 1 2)')
                self.assertEqual((result.returncode, result.stdout.strip(), result.stderr), (0, '3', ''))

    def test_all_starters(self):
        for stage, folder in FOLDERS.items():
            with self.subTest(stage=stage):
                result = subprocess.run([sys.executable, str(ROOT/'examples'/folder/'starter.py'), '--eval', '(square 5)'],
                                        text=True, capture_output=True, timeout=15)
                self.assertEqual((result.returncode, result.stdout.strip()), (0, '25'))

    def test_calculator_cli(self):
        result = subprocess.run([sys.executable, str(ROOT/'examples/08-calculator/calculator.py'), '--eval', '2 + 3 * 4'],
                                text=True, capture_output=True, timeout=15)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, '14'))

    def test_error_exit_no_traceback(self):
        result = cli(9, '--eval', '(/ 1 0)')
        self.assertEqual(result.returncode, 1)
        self.assertIn('division by zero', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_host_repl_recovers_syntax_and_semantic(self):
        result = cli(9, input_text='(+ 1\n(/ 1 0)\n(+ 3 4)\n:quit\n')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '7\n')
        self.assertIn('read error', result.stderr)
        self.assertIn('division by zero', result.stderr)

    def test_eof_quits(self):
        self.assertEqual(cli(9, input_text='').returncode, 0)

    def test_utf8_script_all_supported_stages(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)/'日本語.lisp'
            source.write_text('(define text "日本語")\n(display text)\n(newline)\n(+ 2 3)\n', encoding='utf-8')
            for stage in range(11,16):
                with self.subTest(stage=stage):
                    result = cli(stage, str(source))
                    self.assertEqual((result.returncode, result.stdout), (0, '日本語\n5\n'))

    def test_missing_script_is_user_error(self):
        result = cli(11, 'nonexistent-file.lisp')
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stderr)

    def test_meta_cli_stages(self):
        for stage in range(12,16):
            with self.subTest(stage=stage):
                result = cli(stage, '--meta', '--eval', '(+ 1 (* 2 3))')
                self.assertEqual((result.returncode,result.stdout.strip()), (0,'7'))

    def test_selfhost_repl_recovery_and_state(self):
        for stage in (14,15):
            with self.subTest(stage=stage):
                result = cli(stage, '--selfhost-repl',
                             input_text='(define x 10)\n(+ x 2)\n)\n(/ 1 0)\n(+ x 3)\n:quit\n')
                self.assertEqual(result.returncode, 0)
                self.assertIn('12\n',result.stdout)
                self.assertIn('13\n',result.stdout)
                self.assertIn('error: read error',result.stdout)
                self.assertIn('error: division by zero',result.stdout)

    def test_selfhost_repl_blank_comments_eof(self):
        result = cli(14,'--selfhost-repl',input_text='\n; a comment\n(+ 1 2)\n')
        self.assertEqual(result.returncode,0)
        self.assertIn('3\n',result.stdout)

    def test_selfhost_repl_many_lines_no_stack_growth(self):
        result = cli(14,'--selfhost-repl',input_text='(+ 1 2)\n'*150+':quit\n')
        self.assertEqual(result.returncode,0)
        self.assertEqual(result.stdout, '3\n'*150)

    def test_independent_folder_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            source = ROOT / 'examples/14-selfhosting'
            copied = Path(temp)/'standalone'
            shutil.copytree(source,copied,ignore=shutil.ignore_patterns('__pycache__'))
            result = subprocess.run([sys.executable,str(copied/'lisp.py'),'--meta','--eval','(+ 2 3)'],
                                    text=True,capture_output=True,timeout=15,cwd=temp)
            self.assertEqual((result.returncode,result.stdout.strip()),(0,'5'))

    def test_showcase_command(self):
        result = subprocess.run([sys.executable,str(ROOT/'examples/15-showcase/check_compatibility.py')],
                                text=True,capture_output=True,timeout=15)
        self.assertEqual(result.returncode,0)
        self.assertIn('15/15 compatible cases',result.stdout)


if __name__ == '__main__':
    unittest.main()
