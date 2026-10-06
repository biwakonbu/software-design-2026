"""Execute DFS/BFS and compare the diagrams with observable states."""
from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'examples/07-review'))
from review_data import GRAPH
import flawed_route,improved_route
DATA=json.loads((ROOT/'lectures/data/figures07.json').read_text())
def main():
    calls=[];visited=[];states=[];cursors=[]
    def trace(frame,event,arg):
        if frame.f_code.co_filename==flawed_route.__file__ and frame.f_code.co_name=='visit':
            if event=='call':calls.append(frame.f_locals['vertex'])
            if event=='return':visited.append(set(frame.f_locals['visited']))
        if frame.f_code.co_filename==improved_route.__file__ and event=='line':
            local=frame.f_locals
            if 'vertex' in local and 'queue' in local:states.append((local['vertex'],list(local['queue']),dict(local['previous'])))
            if 'cursor' in local and local.get('path'):cursors.append(list(local['path']))
        return trace
    original={k:list(v) for k,v in GRAPH.items()}
    sys.settrace(trace)
    try:dfs=flawed_route.find_route(GRAPH,'A','D');bfs=improved_route.find_route(GRAPH,'A','D')
    finally:sys.settrace(None)
    assert calls==list('ABEFD') and dfs==list('ABEFD') and visited[-1]==set('ABEF')
    assert bfs==list('ACD')
    assert {f'visit({v})' for v in calls}<={n['label'] for n in DATA[0]['nodes']}
    assert any(v=='E' and q==['D','F'] and p=={'A':None,'B':'A','C':'A','E':'B','D':'C','F':'E'} for v,q,p in states)
    assert ['D'] in cursors and ['D','C'] in cursors and ['D','C','A'] in cursors
    assert '取り出し順 A B C E D' in {n['label'] for n in DATA[1]['nodes']}
    assert 'D 取出し前 queue [D, F]' in {n.get('detail') for n in DATA[1]['nodes']}
    assert '{A,B,E,F}' in {n.get('detail') for n in DATA[0]['nodes']}
    assert {frozenset((a,b)) for a,ns in GRAPH.items() for b in ns}=={frozenset((e['from'],e['to'])) for e in DATA[3]['edges']}
    assert '[A, C, D]' in {n.get('detail') for n in DATA[2]['nodes']}
    changed={k:list(v) for k,v in GRAPH.items()};changed['A']=['C','B'];assert flawed_route.find_route(changed,'A','D')==list('ACD')
    assert improved_route.find_route(GRAPH,'A','F')==list('ABEF') and improved_route.find_route(GRAPH,'A','X') is None
    assert GRAPH==original
    for start,goal,stdout,stderr,code in [('A','D','A -> C -> D\n移動数: 2\n','',0),('A','F','A -> B -> E -> F\n移動数: 3\n','',0),('A','X','','経路なし\n',2)]:
        r=subprocess.run([sys.executable,str(ROOT/'examples/07-review/improved_route.py'),start,goal],capture_output=True,text=True)
        assert (r.stdout,r.stderr,r.returncode)==(stdout,stderr,code),(r.stdout,r.stderr,r.returncode)
    print('Lesson07 DFS calls/visited, BFS queue/parents, reconstruction and CLI: pass')
if __name__=='__main__':main()
