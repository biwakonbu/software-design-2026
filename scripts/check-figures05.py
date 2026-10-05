"""第05回の図を公開グラフ実装の辺・層・実際のBFS状態へ照合する。"""
from pathlib import Path
import importlib.util
import inspect
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'lectures/data/figures05.json').read_text())

def main():
    spec=importlib.util.spec_from_file_location('figure_graphs05',ROOT/'examples/05-graphs/graphs.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    graph=module.DEMO_GRAPH
    edges={tuple(sorted((a,b))) for a,neighbors in graph.items() for b in neighbors}
    assert edges=={tuple(sorted(e)) for e in DATA['edges']}
    for name in ('diamond','adjacency','layersDiagram'):
        assert {tuple(sorted(e)) for e in DATA[name]['edges']}==edges
    assert sorted(n['id'] for n in DATA['adjacency']['nodes'])==sorted(graph)
    assert graph['X']==[]
    observed=[];before={}
    source,start=inspect.getsourcelines(module.shortest_path)
    loop=next(start+i for i,line in enumerate(source) if line.strip()=='while queue:')
    goal=next(start+i for i,line in enumerate(source) if line.strip()=='if vertex == goal:')
    def record(local,node):
        nonlocal before
        parent=local['previous'].copy()
        observed.append({'node':node,'queue':list(local['queue']),'new':{k:v for k,v in parent.items() if k not in before}})
        before=parent
    def watch(frame,event,arg):
        if event=='line' and frame.f_code is module.shortest_path.__code__:
            local=frame.f_locals
            if frame.f_lineno==loop:
                record(local,local.get('vertex','開始'))
            if frame.f_lineno==goal and local['vertex']==local['goal']:
                record(local,local['vertex'])
        return watch
    old=sys.gettrace();sys.settrace(watch)
    try:
        assert module.shortest_path(graph,'A','D')==['A','B','D']
    finally:
        sys.settrace(old)
    assert observed==DATA['trace'],observed
    assert before==DATA['parent']
    layers={vertex: None if (path:=module.shortest_path(graph,'A',vertex)) is None else len(path)-1 for vertex in graph}
    assert layers==DATA['layers']
    assert list(reversed(['D','B','A']))==module.shortest_path(graph,'A','D')
    assert module.bfs(graph,'A')==list('ABCD')
    assert module.dfs(graph,'A')==list('ABDC')
    print('第05回の図・辺・層・発見時の親・BFS状態の照合に合格')

if __name__=='__main__':
    main()
