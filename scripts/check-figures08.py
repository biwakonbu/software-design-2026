"""Compare pictured AST structure, evaluation order and error stages to code."""
from pathlib import Path
import importlib.util,json,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('calculator_figures',ROOT/'examples/08-calculator/calculator.py');calc=importlib.util.module_from_spec(spec);sys.modules[spec.name]=calc;spec.loader.exec_module(calc)
DATA=json.loads((ROOT/'lectures/data/figures08.json').read_text())
def main():
    tree=calc.parse('10-3-2')
    assert isinstance(tree,calc.Binary) and tree.op=='-' and tree.right.value==2
    assert isinstance(tree.left,calc.Binary) and tree.left.op=='-' and tree.left.left.value==10 and tree.left.right.value==3
    assert calc.evaluate(tree)==5 and calc.calculate('8/2/2')==2
    calls=[];returns=[]
    def trace(frame,event,arg):
        if frame.f_code==calc.evaluate.__code__:
            if event=='call':calls.append(frame.f_locals['node'])
            if event=='return':returns.append(arg)
        return trace
    tree=calc.parse('2+3*4');sys.settrace(trace)
    try:value=calc.evaluate(tree)
    finally:sys.settrace(None)
    assert value==14 and returns==[2.,3.,4.,12.,14.]
    assert [n.value for n in calls if isinstance(n,calc.Number)]==[2,3,4]
    assert calc.calculate('(2+3)*4')==20
    ast=calc.parse('2+3*4')
    ast_labels={'r':ast.op,'a':format(ast.left.value,'g'),'m':ast.right.op,'b':format(ast.right.left.value,'g'),'c':format(ast.right.right.value,'g')}
    assert {n['id']:n['label'] for n in DATA[4]['nodes']}==ast_labels
    assert {(e['from'],e['to']) for e in DATA[4]['edges']}=={('r','a'),('r','m'),('m','b'),('m','c')}
    token_node=next(n for n in DATA[5]['nodes'] if n['kind']=='tokens')
    assert token_node['label'].split()==[t.text or 'eof' for t in calc.tokenize('2+3*4')]
    starts={};terms=[]
    def term_trace(frame,event,arg):
        if frame.f_code==calc.Parser.term.__code__:
            if event=='call':starts[id(frame)]=frame.f_locals['self'].pos
            if event=='return':terms.append((starts.pop(id(frame)),frame.f_locals['self'].pos,arg))
        return term_trace
    sys.settrace(term_trace)
    try:calc.parse('2+3*4')
    finally:sys.settrace(None)
    assert [(a,b) for a,b,_ in terms]==[(0,1),(2,5)]
    assert isinstance(terms[0][2],calc.Number) and terms[0][2].value==2
    assert isinstance(terms[1][2],calc.Binary) and terms[1][2].op=='*'
    cases=[('2+3*4','14\n','',0),('2 @ 3','','error: lexical error at column 3: \'@\'\n',1),('2 + * 3','','error: syntax error at column 5: expected number or (\n',1),('1 / 0','','error: semantic error: division by zero\n',1),('(2+3','','error: syntax error at column 5: expected )\n',1),('2 3','','error: syntax error at column 3: unexpected token\n',1)]
    for expression,stdout,stderr,code in cases:
        p=subprocess.run([sys.executable,str(ROOT/'examples/08-calculator/calculator.py'),'--eval',expression],capture_output=True,text=True)
        assert (p.stdout,p.stderr,p.returncode)==(stdout,stderr,code),(expression,p.stdout,p.stderr,p.returncode)
    assert '14.0・CLI 14' in {n.get('detail') for n in DATA[1]['nodes']}
    assert 'column 3: \'@\'' in {n.get('detail') for n in DATA[2]['nodes']}
    print('Lesson08 left-associative AST, recursive return order, lexical/syntax/semantic CLI: pass')
if __name__=='__main__':main()
