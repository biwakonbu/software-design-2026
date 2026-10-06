"""Check environments, list recursion and script/REPL contracts independently."""
import itertools, math, subprocess, sys, tempfile, unittest
from pathlib import Path
from lisp import Interpreter, LispError, Symbol, format_value, read_all

class FlowTests(unittest.TestCase):
    def run_cli(self, *args, input=None, cwd=None):
        return subprocess.run([sys.executable, str(Path(__file__).with_name('lisp.py').resolve()), *args], input=input, text=True, capture_output=True, cwd=cwd, timeout=20)
    def test_closures(self):
        i=Interpreter();i.execute('(define x 100)');i.execute('(define f (lambda (x) (+ x 1)))')
        self.assertIs(i.environment['f'].environment,i.environment)
        self.assertEqual(i.execute('(f 4)'),5);self.assertEqual(i.execute('x'),100)
        i.execute('(define make-adder (lambda (x) (lambda (y) (+ x y))))')
        i.execute('(define add5 (make-adder 5))');i.execute('(define add7 (make-adder 7))')
        a=i.environment['add5'];b=i.environment['add7']
        self.assertIsNot(a.environment,b.environment);self.assertIs(a.environment.parent,i.environment)
        self.assertEqual(a.environment['x'],5);self.assertEqual(b.environment['x'],7)
        self.assertEqual(i.execute('(add5 3)'),8);self.assertEqual(i.execute('(add7 3)'),10)
        with self.assertRaisesRegex(LispError,'unknown symbol'):i.execute('missing')
        with self.assertRaises(LispError):i.execute('(f 1 2)')
    def test_recursion(self):
        i=Interpreter();i.execute('(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))')
        for n in range(8):self.assertEqual(i.execute(f'(fact {n})'),math.factorial(n))
        i.execute('(define total (lambda (xs) (if (null? xs) 0 (+ (car xs) (total (cdr xs))))))')
        count=0
        for size in range(6):
            for xs in itertools.product(range(-1,2),repeat=size):
                data=' '.join(map(str,xs));self.assertEqual(i.execute(f'(total (quote ({data})))'),sum(xs));count+=1
        self.assertEqual(count,364)
    def test_data(self):
        forms=read_all('(display "a (b); c") ; memo\n');self.assertEqual(len(forms),1);self.assertIsInstance(forms[0][0],Symbol);self.assertIs(type(forms[0][1]),str);self.assertEqual(forms[0][1],'a (b); c')
        i=Interpreter();i.execute('(define xs (quote (10 20 30)))')
        self.assertEqual(format_value(i.execute('(cons 5 (cdr xs))')),'(5 20 30)');self.assertEqual(format_value(i.execute('xs')),'(10 20 30)')
        with self.assertRaises(LispError):read_all('"unfinished')
        with self.assertRaises(LispError):i.execute('(car (list))')
    def test_script(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'demo.lisp'
            path.write_text('(define square (lambda (x) (* x x)))\n(display (square 5))\n(newline)\n(display (square 7))\n(newline)\n',encoding='utf-8')
            r=self.run_cli('demo.lisp',cwd=folder);self.assertEqual((r.stdout,r.stderr,r.returncode),('25\n49\n()\n','',0))
            path.write_text('(display 25)\n(+ 1',encoding='utf-8');r=self.run_cli('demo.lisp',cwd=folder);self.assertEqual((r.stdout,r.returncode),('',1));self.assertIn('unclosed (',r.stderr)
            path.write_text('(display 25)\nmissing',encoding='utf-8');r=self.run_cli('demo.lisp',cwd=folder);self.assertEqual((r.stdout,r.stderr,r.returncode),('25','error: unknown symbol: missing\n',1))
    def test_repl_cli(self):
        r=self.run_cli(input='(define x 5)\n(/ 1 0)\n(+ x 3)\n:quit\n');self.assertEqual((r.stdout,r.stderr,r.returncode),('x\n8\n','error: division by zero\n',0))
        r=self.run_cli(input='');self.assertEqual((r.stdout,r.stderr,r.returncode),('','',0))
        r=self.run_cli('--eval','(if #f (/ 1 0) 7)');self.assertEqual((r.stdout,r.stderr,r.returncode),('7\n','',0))
        r=self.run_cli('--eval','(+ #t 1)');self.assertEqual((r.stdout,r.returncode),('',1));self.assertIn('expected number',r.stderr)
        r=self.run_cli('--unknown');self.assertEqual((r.stdout,r.returncode),('',2));self.assertIn('usage:',r.stderr)

if __name__=='__main__':unittest.main()
