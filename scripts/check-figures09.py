"""Compare reader positions, head/argument order, and REPL recovery with code."""
from pathlib import Path
import importlib.util,json,sys,subprocess,io
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lisp_figures',ROOT/'examples/09-lisp-arithmetic/lisp.py');lisp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lisp;spec.loader.exec_module(lisp)
DATA=json.loads((ROOT/'lectures/data/figures09.json').read_text())
def main():
    positions=[];returns=[];expressions=[];applied=[]
    def trace(frame,event,arg):
        if frame.f_code.co_filename==lisp.__file__:
            if frame.f_code.co_name=='read':
                if event=='call':positions.append(frame.f_locals['pos'])
                if event=='return':returns.append((frame.f_locals['pos'],arg))
            if frame.f_code==lisp.Interpreter.evaluate.__code__ and event=='call':expressions.append(frame.f_locals['expression'])
            if frame.f_code==lisp.Interpreter.call.__code__ and event=='call':applied.append((frame.f_locals['function'].name,frame.f_locals['args']))
        return trace
    sys.settrace(trace)
    try:forms=lisp.read_all('(+ 1 (* 2 3))');value=lisp.Interpreter().evaluate(forms[0])
    finally:sys.settrace(None)
    assert positions==[0,1,2,3,4,5,6]
    assert (8,[lisp.Symbol('*'),2,3]) in returns and (9,[lisp.Symbol('+'),1,[lisp.Symbol('*'),2,3]]) in returns
    assert [t.text for t in lisp.tokenize('(+ 1 (* 2 3))')]==['(','+','1','(','*','2','3',')',')']
    assert value==7 and applied==[('*',[2,3]),('+',[1,6])]
    form=forms[0]
    assert {n['id']:n['label'] for n in DATA[3]['nodes']}=={'r':str(form[0]),'a':str(form[1]),'m':str(form[2][0]),'b':str(form[2][1]),'c':str(form[2][2])}
    assert {(e['from'],e['to']) for e in DATA[3]['edges']}=={('r','a'),('r','m'),('m','b'),('m','c')}
    assert expressions==[forms[0],lisp.Symbol('+'),1,forms[0][2],lisp.Symbol('*'),2,3]
    assert lisp.Interpreter().execute('(- 10 2 3)')==5
    machine=lisp.Interpreter(stdin=io.StringIO('(+ 2 3)\n(/ 1 0)\n(* 4 5)\n'),stdout=io.StringIO(),stderr=io.StringIO())
    assert lisp.repl(machine)==0 and machine.stdout.getvalue()=='5\n20\n' and machine.stderr.getvalue()=='error: division by zero\n'
    file=str(ROOT/'examples/09-lisp-arithmetic/lisp.py')
    for expression,stdout,stderr,code in [('(+ 1 (* 2 3))','7\n','',0),('(+ 1 2))','','error: read error at offset 7: unexpected )\n',1)]:
        p=subprocess.run([sys.executable,file,'--eval',expression],capture_output=True,text=True);assert (p.stdout,p.stderr,p.returncode)==(stdout,stderr,code)
    p=subprocess.run([sys.executable,file],input='(+ 2 3)\n(/ 1 0)\n(* 4 5)\n',capture_output=True,text=True);assert (p.stdout,p.stderr,p.returncode)==('5\n20\n','error: division by zero\n',0)
    assert '0 1 2 3 4 5 6 7 8' in {n.get('detail') for n in DATA[0]['nodes']}
    assert 'error: division by zero' in {n.get('detail') for n in DATA[2]['nodes']}
    print('Lesson09 reader pos/returns, evaluation/application order, REPL recovery/CLI: pass')
if __name__=='__main__':main()
