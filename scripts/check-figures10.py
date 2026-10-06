from pathlib import Path
import importlib.util,sys,io,json
ROOT=Path(__file__).resolve().parents[1]
def load(id,name):
 spec=importlib.util.spec_from_file_location('next_'+id,ROOT/f'examples/{name}/lisp.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
r=[]
m=load('10','10-lisp-functions');machine=m.Interpreter()
for source,expected in [('(define width (+ 2 3))','width'),('width','5'),('(define x 100)','x'),('(define f (lambda (x) (+ x 1)))','f'),('(define g (lambda (y) (+ x y)))','g'),('(f 4)','5'),('x','100'),('(g 4)','104'),('(if #f (/ 1 0) 7)','7')]:
 value=m.format_value(machine.execute(source));assert value==expected;(r.append({'lesson':'10','source':source,'result':value}))
assert machine.environment['f'].environment is machine.environment
try:machine.execute('(if 0 (/ 1 0) 7)')
except m.LispError as e:assert str(e)=='division by zero';r.append({'lesson':'10','source':'(if 0 (/ 1 0) 7)','error':str(e)})
else:raise AssertionError('zero is true in this dialect')

# Observe the preserved make-adder figures and recursive descent/return.
machine=m.Interpreter()
assert m.format_value(machine.execute('(define make-adder (lambda (x) (lambda (y) (+ x y))))'))=='make-adder'
global_env=machine.environment;make=global_env['make-adder'];assert make.environment is global_env
machine.execute('(define add5 (make-adder 5))');add5=global_env['add5'];saved=add5.environment
assert saved['x']==5 and saved.parent is global_env
frames=[];original_sequence=machine.sequence
def observe(forms,env,depth):
    if 'y' in env:frames.append((dict(env),env.parent))
    return original_sequence(forms,env,depth)
machine.sequence=observe
assert m.format_value(machine.execute('(add5 3)'))=='8';assert frames[-1][0]['y']==3 and frames[-1][1] is saved
machine.execute('(define add7 (make-adder 7))');assert machine.execute('(add7 3)')==10 and machine.execute('(add5 3)')==8
machine.execute('(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))')
calls=[];returns=[]
def trace(frame,event,arg):
    if frame.f_code.co_filename==m.__file__ and frame.f_code.co_name=='sequence':
        env=frame.f_locals.get('env',{})
        if 'n' in env:
            if event=='call':calls.append(env['n']);assert env.parent is global_env
            if event=='return':returns.append(arg)
    return trace
sys.settrace(trace)
try:assert machine.execute('(fact 2)')==2
finally:sys.settrace(None)
assert calls==[2,1,0] and returns==[1,1,2]
assert machine.execute('(fact 4)')==24
r.append({'closure_frames':True,'fact_descent':calls,'fact_returns':returns})
print(sys.version.split()[0],len(r),'Lesson10 design states pass')
