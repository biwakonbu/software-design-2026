"""A bounded independent arithmetic oracle, reader and public CLI contracts."""
from itertools import product
from pathlib import Path
from fractions import Fraction
import subprocess,sys,unittest,io
import lisp
class LispContract(unittest.TestCase):
    def test_arithmetic(self):
        m=lisp.Interpreter()
        for a,b,c in product(range(-2,3),repeat=3):
            self.assertEqual(m.execute(f'(+ {a} (* {b} {c}))'),a+b*c)
            self.assertEqual(m.execute(f'(* (+ {a} {b}) {c})'),(a+b)*c)
            self.assertEqual(m.execute(f'(- {a} {b} {c})'),a-b-c)
        for a,b in product(range(-4,5),repeat=2):
            if b:self.assertAlmostEqual(m.execute(f'(/ {a} {b})'),float(Fraction(a,b)))
        self.assertEqual(m.execute('(+)'),0);self.assertEqual(m.execute('(*)'),1)
        self.assertEqual(m.execute('(- 3)'),-3);self.assertEqual(m.execute('(/ 2)'),.5)
    def test_reader(self):
        tokens=lisp.tokenize('(+ 1 (* 2 3))');self.assertEqual([t.text for t in tokens],['(','+','1','(','*','2','3',')',')'])
        self.assertEqual(lisp.read_one('(+ 1 (* 2 3))'),[lisp.Symbol('+'),1,[lisp.Symbol('*'),2,3]])
        self.assertEqual(lisp.Interpreter().execute('(+ 1 ;comment\n 2)'),3)
        for source in ['', '(+ 1 2', '(+ 1 2))']:
            with self.subTest(source=source),self.assertRaises(lisp.LispError):lisp.read_one(source)
    def test_language_boundaries(self):
        m=lisp.Interpreter()
        for source in ['(/ 1 0)','(-)','(/)','(unknown 1)','()','(+ 1 #t)','"abc"','(define x 1)','(+ 1 2) (+ 3 4)','1e999','(* 1e308 1e308)']:
            with self.subTest(source=source),self.assertRaises(lisp.LispError):m.execute(source)
    def test_repl_recovery(self):
        m=lisp.Interpreter(stdin=io.StringIO('(+ 2 3)\n(/ 1 0)\n(* 4 5)\n'),stdout=io.StringIO(),stderr=io.StringIO())
        self.assertEqual(lisp.repl(m),0);self.assertEqual(m.stdout.getvalue(),'5\n20\n');self.assertEqual(m.stderr.getvalue(),'error: division by zero\n')
    def test_cli(self):
        script=str(Path(__file__).with_name('lisp.py'))
        for source,stdout,stderr,code in [('(+ 1 (* 2 3))','7\n','',0),('(- 10 2 3)','5\n','',0),('(+ 1 2))','','error: read error at offset 7: unexpected )\n',1),('(/ 1 0)','','error: division by zero\n',1)]:
            r=subprocess.run([sys.executable,script,'--eval',source],capture_output=True,text=True);self.assertEqual((r.stdout,r.stderr,r.returncode),(stdout,stderr,code))
        r=subprocess.run([sys.executable,script],input='(+ 2 3)\n(/ 1 0)\n(* 4 5)\n',capture_output=True,text=True);self.assertEqual((r.stdout,r.stderr,r.returncode),('5\n20\n','error: division by zero\n',0))
        self.assertEqual(subprocess.run([sys.executable,script,'--unknown'],capture_output=True).returncode,2)
        r=subprocess.run([sys.executable,script],input='(+ 2 3)\n:quit\n(/ 1 0)\n',capture_output=True,text=True);self.assertEqual((r.stdout,r.stderr,r.returncode),('5\n','',0))
if __name__=='__main__':unittest.main(verbosity=2)
