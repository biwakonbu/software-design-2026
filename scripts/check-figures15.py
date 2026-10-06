from pathlib import Path
import importlib.util,sys,io,json,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
def load(id,name):
 s=importlib.util.spec_from_file_location('figure_'+id,ROOT/f'examples/{name}/lisp.py');m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
observations=[]
m=load('15','15-showcase');i=m.Interpreter();assert m.format_value(i.execute('(begin (define x 100) (define f (lambda (x) (+ x 1))) (f 4) x)'))=='100';observations.append({'lesson':'15','global_after_call':'100'})
for meta in [False,True]:
 i=m.Interpreter();assert m.format_value(i.meta_evaluate("'()") if meta else i.execute("'()"))=='()'
 try:i.meta_evaluate('(car (list))') if meta else i.execute('(car (list))')
 except m.LispError as e:assert 'car: empty list' in str(e)
 else:raise AssertionError('empty car must fail')
 observations.append({'lesson':'15','meta':meta,'empty_list':'()','empty_car_error':'car: empty list'})
r=subprocess.run([sys.executable,str(ROOT/'examples/15-showcase/check_compatibility.py')],text=True,capture_output=True,timeout=20);assert r.returncode==0 and r.stdout.endswith('15/15 compatible cases\n') and not r.stderr;observations.append({'lesson':'15','compatibility':'15/15','stderr':'','exit':0})
print(sys.version.split()[0],len(observations),'Lesson15 observed states pass')
