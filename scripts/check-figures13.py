from pathlib import Path
import importlib.util,sys,io,json,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
def load(id,name):
 s=importlib.util.spec_from_file_location('figure_'+id,ROOT/f'examples/{name}/lisp.py');m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
observations=[]
m=load('13','13-language-review')
source='(begin (define x 10) (define f (lambda (y) (+ x y))) ((lambda (x) (f 1)) 99))'
for meta in [False,True]:
 for expr,value in [(source,'11'),(source.replace('x 10','x 20'),'21'),('(if #f (/ 1 0) 8)','8')]:
  i=m.Interpreter();v=m.format_value(i.meta_evaluate(expr) if meta else i.execute(expr));assert v==value;observations.append({'lesson':'13','meta':meta,'source':expr,'result':v})
 expr='(begin (define my-if (lambda (c a b) (if c a b))) (my-if #f (/ 1 0) 8))'
 i=m.Interpreter()
 try:i.meta_evaluate(expr) if meta else i.execute(expr)
 except m.LispError as e:assert str(e)=='division by zero';observations.append({'lesson':'13','meta':meta,'source':expr,'error':str(e)})
 else:raise AssertionError('eager arguments must fail')
i=m.Interpreter(trace=True,stderr=io.StringIO());assert m.format_value(i.meta_evaluate('(+ 1 (* 2 3))'))=='7'
lines=[x for x in i.stderr.getvalue().splitlines() if x.startswith('[meta ')]
assert lines==['[meta depth=0] (+ 1 (* 2 3))','[meta depth=1] +','[meta depth=1] 1','[meta depth=1] (* 2 3)','[meta depth=2] *','[meta depth=2] 2','[meta depth=2] 3'];observations.append({'lesson':'13','meta_trace':lines,'stdout':'7'})
i=m.Interpreter(trace=True,stderr=io.StringIO());assert m.format_value(i.meta_evaluate('((lambda (x) (+ x 1)) 4)'))=='5';observations.append({'lesson':'13','source':'((lambda (x) (+ x 1)) 4)','meta_trace':[x for x in i.stderr.getvalue().splitlines() if x.startswith('[meta ')]})
print(sys.version.split()[0],len(observations),'Lesson13 observed states pass')
