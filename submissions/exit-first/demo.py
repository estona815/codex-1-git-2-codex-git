"""Five reproducible synthetic examples. Run: python demo.py"""
import copy
import json
from exit_first import evaluate

def examples():
    base = dict(width=8, height=5, footprint=[2, 2], start=[0, 1], goal=[6, 1], permanent=[], movable=[], margin_cells=0)
    opened = copy.deepcopy(base)
    shelf = copy.deepcopy(base)
    shelf['movable'] = [dict(id='shelf-A', cells=[[3, y] for y in range(5)])]
    wall = copy.deepcopy(base)
    wall['permanent'] = [[3, y] for y in range(5)]
    missing = copy.deepcopy(base)
    del missing['footprint']
    detour = dict(width=7, height=5, footprint=[1, 1], start=[0, 2], goal=[6, 2], permanent=[], movable=[dict(id='box', cells=[[3, 2]])])
    return [('Open space', opened), ('Removable shelf', shelf), ('Fixed wall', wall), ('Missing dimensions', missing), ('Fewer removals before shorter distance', detour)]

def draw(data, result):
    cells = [['.' for _ in range(data['width'])] for _ in range(data['height'])]
    for x, y in data['permanent']:
        cells[y][x] = '#'
    for obj in data['movable']:
        for x, y in obj['cells']:
            cells[y][x] = 'm'
    for x, y in result['path']:
        cells[y][x] = '*'
    x, y = data['start']; cells[y][x] = 'S'
    x, y = data['goal']; cells[y][x] = 'G'
    return '\n'.join(' '.join(row) for row in cells)

if __name__ == '__main__':
    print('EXIT FIRST | Synthetic grid demonstration | NOT a physical safety assessment')
    print('Legend: # fixed, m removable, * route anchor, S start, G target anchor. Footprint has area; * is anchor only.')
    for title, data in examples():
        result = evaluate(data)
        print('\n' + title + '\n' + '=' * len(title))
        print(draw(data, result))
        print(json.dumps(result, ensure_ascii=False, indent=2))
