from pathlib import Path
import importlib.util,sys,io,json
ROOT=Path(__file__).resolve().parents[1]
def load(id,name):
 spec=importlib.util.spec_from_file_location('next_'+id,ROOT/f'examples/{name}/lisp.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
r=[]
m=load('12','12-meta-evaluator');machine=m.Interpreter()
for source,expected in [('(quote x)','x'),('(if #f (/ 1 0) 7)','7'),('(if 0 7 (/ 1 0))','7'),('(+ 1 (* 2 3))','7')]:
 value=m.format_value(machine.meta_evaluate(source));assert value==expected;r.append({'lesson':'12','source':source,'result':value})
for source,error in [('x','stage 12 meta: unknown symbol'),('(car (quote (1)))','stage 12 meta: only arithmetic, quote, if')]:
 try:machine.meta_evaluate(source)
 except m.LispError as e:assert str(e)==error;r.append({'lesson':'12','source':source,'error':str(e)})
 else:raise AssertionError('unsupported expression must fail')

# Observe values crossing the host arithmetic boundary in evaluation order.
machine=m.Interpreter();applied=[];original_apply=machine.apply_builtin
machine.load_meta()
def observe(function,args):
    if isinstance(function,m.Builtin) and function.name in ['+','-','*','/']:
        applied.append((function.name,list(args)))
    return original_apply(function,args)
machine.add_builtin('apply',observe,2,2)
assert machine.meta_evaluate('(* (+ 1 2) (- 9 4))')==15
assert applied==[('+',[1,2]),('-',[9,4]),('*',[3,5])]
r.append({'arithmetic_boundary':applied,'result':15})
print(sys.version.split()[0],len(r),'Lesson12 design states pass')
