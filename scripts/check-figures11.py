from pathlib import Path
import importlib.util,sys,io,json
ROOT=Path(__file__).resolve().parents[1]
def load(id,name):
 spec=importlib.util.spec_from_file_location('next_'+id,ROOT/f'examples/{name}/lisp.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
r=[]
m=load('11','11-lisp-scripts');machine=m.Interpreter(stdout=io.StringIO())
for source,expected in [('(list (+ 1 2) 4)','(3 4)'),('(quote ((+ 1 2) 4))','((+ 1 2) 4)'),('(list? (car (quote ((+ 1 2) 4))))','#t'),('(car (quote (+ 1 2)))','+'),('(cdr (quote (+ 1 2)))','(1 2)'),('(symbol? (car (quote (+ 1 2))))','#t'),('(list? (car (cdr (quote (* (+ 1 2) 4)))))','#t')]:
 value=m.format_value(machine.execute(source));assert value==expected;r.append({'lesson':'11','source':source,'result':value})
try:machine.execute('(display 25)(+ 1')
except m.LispError as e:assert str(e)=='read error at offset 12: unclosed (' and machine.stdout.getvalue()=='';r.append({'lesson':'11','source':'(display 25)(+ 1','error':str(e),'stdout':''})
else:raise AssertionError('parse failure required before sequence')

# The cdr/cons diagram describes new lists, retaining the source list.
machine=m.Interpreter();machine.execute('(define xs (quote (10 20 30)))')
assert m.format_value(machine.execute('(car xs)'))=='10'
assert m.format_value(machine.execute('(cdr xs)'))=='(20 30)'
assert m.format_value(machine.execute('(cons 5 (cdr xs))'))=='(5 20 30)'
assert m.format_value(machine.execute('xs'))=='(10 20 30)'
forms=m.read_all('(display "a (b); c") ; memo\n')
assert len(forms)==1 and type(forms[0][1]) is str and forms[0][1]=='a (b); c'
r.append({'list_source_unchanged':True,'lexer_string_comment':True})
print(sys.version.split()[0],len(r),'Lesson11 design states pass')
