"""第06回の仕様表を参考版・意図的な未完成スターターの実CLIへ照合する。"""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'lectures/data/figures06.json').read_text())

def main():
    directory=ROOT/'examples/06-route-project'
    sys.path.insert(0,str(directory))
    import route_data,route_reference
    graph=route_data.GRAPH
    assert sorted(graph)==sorted(n['id'] for n in DATA['nodes'])
    assert {tuple(sorted((a,b))) for a,neighbors in graph.items() for b in neighbors}=={tuple(sorted(e)) for e in DATA['edges']}
    assert graph['X']==[]
    for row in DATA['outcomes']:
        actual=subprocess.run([sys.executable,str(directory/'route_reference.py'),*row['args']],capture_output=True,text=True)
        assert (actual.stdout,actual.stderr,actual.returncode)==(row['stdout'],row['stderr'],row['exit']),row
        if row['result']=='ValueError':
            try:route_reference.find_route(graph,*row['args'])
            except ValueError:pass
            else:raise AssertionError('ValueError expected')
        else:
            assert route_reference.find_route(graph,*row['args'])==row['result']
    for args,code in [(('A','A'),0),(('A','B'),0),(('A','D'),2),(('D','A'),2),(('A','X'),2),(('UNKNOWN','D'),2)]:
        actual=subprocess.run([sys.executable,str(directory/'route_starter.py'),*args],capture_output=True,text=True)
        assert actual.returncode==code
        if args==('A','D'):
            assert actual.stdout=='' and actual.stderr=='経路なし（starterは多段経路未実装）: A → D\n'
    assert route_reference.find_route(graph,'D','A')==list('DBA')
    print('第06回の図・架空駅の辺・正常/境界/失敗の関数結果とCLI契約に合格')

if __name__=='__main__':
    main()
