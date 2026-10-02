"""Compare host and Lisp evaluator on declared fixtures."""
import json
from pathlib import Path
from lisp import Interpreter, LispError, format_value

def main():
    cases = json.loads(Path(__file__).with_name('compatibility.json').read_text(encoding='utf-8'))
    failures = 0
    for index, case in enumerate(cases, 1):
        outcomes = []
        for meta in (False, True):
            machine = Interpreter()
            try:
                value = machine.meta_evaluate(case['source']) if meta else machine.execute(case['source'])
                outcomes.append('expected' in case and format_value(value) == case['expected'])
            except LispError as error:
                outcomes.append('error' in case and case['error'] in str(error))
        passed = all(outcomes)
        failures += not passed
        print(f'{index:02} {"PASS" if passed else "FAIL"}: {case["source"]}')
    print(f'{len(cases) - failures}/{len(cases)} compatible cases')
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
