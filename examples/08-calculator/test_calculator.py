"""Deterministic checks of a bounded arithmetic domain and public CLI contracts."""
from itertools import product
from pathlib import Path
from fractions import Fraction
import subprocess,sys,unittest
import calculator as c
class CalculatorContract(unittest.TestCase):
    def test_precedence_and_parentheses(self):
        for a,b,d in product(range(-2,3),repeat=3):
            for first,second in product(['+','-','*'],repeat=2):
                # Independent grammar oracle: multiplication precedes addition/subtraction;
                # equal precedence evaluates left to right. No eval/exec.
                def op(x,y,s):return x+y if s=='+' else x-y if s=='-' else x*y
                expected=op(a,op(b,d,second),first) if second=='*' and first!='*' else op(op(a,b,first),d,second)
                with self.subTest(a=a,b=b,d=d,first=first,second=second):
                    self.assertEqual(c.calculate(f'({a}){first}({b}){second}({d})'),expected)
                    self.assertEqual(c.calculate(f'(({a}){first}({b})){second}({d})'),op(op(a,b,first),d,second))
                    self.assertEqual(c.calculate(f'({a}){first}(({b}){second}({d}))'),op(a,op(b,d,second),first))
    def test_division_and_ast(self):
        for a,b in product(range(-4,5),repeat=2):
            if b:self.assertAlmostEqual(c.calculate(f'({a})/({b})'),float(Fraction(a,b)))
        self.assertEqual(c.calculate('8/2/2'),2)
        self.assertEqual(c.calculate('.5 + 3.'),3.5)
        self.assertEqual(c.calculate('--3'),3)
        tree=c.parse('10-3-2');self.assertIsInstance(tree.left,c.Binary);self.assertEqual(tree.op,'-');self.assertEqual(tree.right.value,2)
    def test_error_stages(self):
        for source,stage in [('2 @ 3','lexical'),('','syntax'),('2 + * 3','syntax'),('(2+3','syntax'),('2 3','syntax'),('1/0','semantic')]:
            with self.subTest(source=source),self.assertRaisesRegex(c.CalculatorError,stage):c.calculate(source)
    def test_cli(self):
        script=str(Path(__file__).with_name('calculator.py'))
        for source,stdout,stderr,code in [('2+3*4','14\n','',0),('(2+3)*4','20\n','',0),('10-3-2','5\n','',0),('2 @ 3','','error: lexical error at column 3: \'@\'\n',1),('2 + * 3','','error: syntax error at column 5: expected number or (\n',1),('1/0','','error: semantic error: division by zero\n',1)]:
            result=subprocess.run([sys.executable,script,'--eval',source],capture_output=True,text=True)
            self.assertEqual((result.stdout,result.stderr,result.returncode),(stdout,stderr,code))
        self.assertEqual(subprocess.run([sys.executable,script],capture_output=True).returncode,2)
if __name__=='__main__':unittest.main(verbosity=2)
