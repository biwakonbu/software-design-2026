from pathlib import Path
import importlib.util,sys,io,json,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
def load(id,name):
 s=importlib.util.spec_from_file_location('figure_'+id,ROOT/f'examples/{name}/lisp.py');m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
observations=[]
m=load('14','14-selfhosting');i=m.Interpreter();i.load_meta();env=i.meta_environment;cell=env[0];old=cell[0]
i.meta_evaluate('(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))')
assert env[0] is cell and cell[0] is not old;closure=cell[0][0][1];assert str(closure[0])=='closure' and closure[3] is env and [str(x) for x in closure[1]]==['n'];assert m.format_value(i.meta_evaluate('(fact 4)'))=='24';observations.append({'lesson':'14','shared_cell_identity':True,'binding_list_replaced':True,'captured_env_identity':True,'fact4':'24'})
for expr,value in [('(begin (define g (lambda () n)) (define n 1) (g))','1'),('((lambda (x y) (+ x y)) 2 3)','5'),('(begin (define square (lambda (x) (* x x))) (square 6))','36')]:
 i=m.Interpreter();assert m.format_value(i.meta_evaluate(expr))==value;observations.append({'lesson':'14','source':expr,'result':value})
r=subprocess.run([sys.executable,str(ROOT/'examples/14-selfhosting/lisp.py'),'--selfhost-repl'],input='(define x 5)\n(car (list))\n(+ x 3)\n:quit\n',text=True,capture_output=True,timeout=20)
assert (r.stdout,r.stderr,r.returncode)==('x\nerror: car: empty list\n8\n','',0),(r.stdout,r.stderr,r.returncode);observations.append({'lesson':'14','repl_stdout':r.stdout,'stderr':r.stderr,'exit':r.returncode})
print(sys.version.split()[0],len(observations),'Lesson14 observed states pass')
