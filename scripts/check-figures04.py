"""図の値を、公開実装とスライドの実コードから読み取った状態へ照合する。"""
from pathlib import Path
import ast
import contextlib
import importlib.util
import inspect
import io
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'lectures/data/figures04.json').read_text())
SOURCE = (ROOT / 'lectures/04.md').read_text()

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'examples/04-algorithms' / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def block(heading):
    tail = SOURCE.split('# ' + heading + '\n', 1)[1]
    return re.search(r'```python\n(.*?)\n```', tail, re.S).group(1)

def trace_call(function, args, callback):
    old = sys.gettrace()
    sys.settrace(callback)
    try:
        return function(*args)
    finally:
        sys.settrace(old)

def interval_states(function, names):
    states = []
    source, start = inspect.getsourcelines(function) if function.__code__.co_filename != '<lecture04>' else (block('二分探索の全体：半開区間').splitlines(True), 1)
    comparison = next(start + i for i, line in enumerate(source) if f'if {"a[mid]" if names[0]=="lo" else "values[middle]"} == target:' in line)
    terminal = next(start + i for i, line in enumerate(source) if line.strip() == 'return None')
    def observe(frame, event, arg):
        if event == 'line' and frame.f_code is function.__code__ and frame.f_lineno in (comparison, terminal):
            values = frame.f_locals
            states.append([values[names[0]], values[names[1]], values[names[2]] if frame.f_lineno == comparison else None])
        return observe
    assert trace_call(function, (DATA['values'], DATA['target']), observe) is None
    return states

def main():
    sorting = load('figure_sorting04', 'sorting_search.py')
    trees = load('figure_trees04', 'trees.py')
    memory = load('figure_memory04', 'memory_complexity.py')
    namespace = {}
    exec(compile(block('二分探索の全体：半開区間'), '<lecture04>', 'exec'), namespace)
    assert interval_states(namespace['binary_search'], ('lo','hi','mid')) == DATA['halfOpen']
    assert interval_states(sorting.binary_search, ('low','high','middle')) == DATA['closed']
    calls = []
    def visit(frame, event, arg):
        if event == 'line' and frame.f_code.co_name == 'visit' and frame.f_code.co_filename == trees.__file__:
            line = Path(trees.__file__).read_text().splitlines()[frame.f_lineno-1].strip()
            if line == 'result.append(node.value)':
                names=[]; cursor=frame
                while cursor:
                    if cursor.f_code.co_name == 'visit' and cursor.f_code.co_filename == trees.__file__:
                        names.append(cursor.f_locals['node'].value)
                    cursor=cursor.f_back
                calls.append(names[::-1])
        return visit
    assert trace_call(trees.dfs, (trees.demo_tree(),), visit) == DATA['dfs']
    assert calls == DATA['dfsCalls']
    queues=[]
    def queue(frame,event,arg):
        if event=='line' and frame.f_code is trees.bfs.__code__:
            line=Path(trees.__file__).read_text().splitlines()[frame.f_lineno-1].strip()
            if line=='while queue:' and frame.f_locals['result']:
                queues.append([n.value for n in frame.f_locals['queue']])
        return queue
    assert trace_call(trees.bfs,(trees.demo_tree(),),queue)==DATA['bfs']
    assert queues==DATA['bfsAfter']
    root=trees.demo_tree();edges=[];nodes=[]
    def walk(n):
        nodes.append(n.value)
        for child in n.children:
            edges.append([n.value,child.value]);walk(child)
    walk(root)
    assert sorted(nodes)==sorted(n['name'] for n in DATA['treeNodes'])
    assert sorted(edges)==sorted(DATA['treeEdges'])
    for name, variable, key in [('スタック','stack','stack'),('キュー','queue','queue')]:
        state={};results=[]
        for statement in ast.parse(block(name)).body:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(ast.Module(body=[statement],type_ignores=[]),'<container04>','exec'),state)
            text=ast.unparse(statement)
            if variable in state and ('.append(' in text or '.pop(' in text or '.popleft(' in text or ('deque([' in text)):
                results.append(list(state[variable]))
        assert results==DATA[key], (key,results)
    for row in DATA['growth']:
        assert [memory.comparison_counts(n)[row['key']] for n in (8,16,32)]==row['values']
    changed=block('幅優先探索 BFS').replace('queue.popleft()', 'queue.pop()')
    children={}
    def child_map(n):
        children[n.value]=[c.value for c in n.children]
        for child in n.children:child_map(child)
    child_map(root);ns={'children':children}
    exec(changed,ns);assert ns['order']==list('ACFBED')
    for name, count in [('containers.py',3),('trees.py',2)]:
        output=subprocess.check_output([sys.executable,str(ROOT/'examples/04-algorithms'/name)],text=True)
        expected='\n'.join(output.splitlines()[:count])
        assert expected in SOURCE
    print('第04回の図・スライド実コード・公開実装・出力の状態照合に合格')

if __name__=='__main__':
    main()
