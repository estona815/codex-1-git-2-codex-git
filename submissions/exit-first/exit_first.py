"""EXIT FIRST: bounded, synthetic-grid removal feasibility research spike.

No network, AI service, registration, file upload, or physical equipment control.
Movable objects in a result are assumed removed off-plan BEFORE the route starts.
This is NOT a relocation schedule, continuous-space planner, or safety approval.
"""
from __future__ import annotations
import argparse
import heapq
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Cell = tuple[int, int]

class InputError(ValueError):
    """Invalid or contradictory layout; never silently treated as free space."""

@dataclass(frozen=True)
class Layout:
    width: int
    height: int
    footprint: Cell
    start: Cell
    goal: Cell
    permanent: frozenset[Cell]
    movable: tuple[tuple[str, frozenset[Cell]], ...]
    margin: int = 0


def integer(value: Any, name: str, lo: int, hi: int) -> int:
    if type(value) is not int or not lo <= value <= hi:
        raise InputError(f'{name} must be an integer in [{lo}, {hi}]')
    return value


def pair(value: Any, name: str, lo: int = 0, hi: int = 29) -> Cell:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise InputError(f'{name} must contain exactly two integers')
    return (integer(value[0], name + '[0]', lo, hi),
            integer(value[1], name + '[1]', lo, hi))


def occupied(layout: Layout, position: Cell) -> frozenset[Cell]:
    x, y = position
    w, h = layout.footprint
    m = layout.margin
    return frozenset((a, b) for a in range(x-m, x+w+m)
                     for b in range(y-m, y+h+m))


def valid_area(layout: Layout, position: Cell) -> bool:
    x, y = position
    w, h = layout.footprint
    m = layout.margin
    return x-m >= 0 and y-m >= 0 and x+w+m <= layout.width and y+h+m <= layout.height


def load_layout(data: Any) -> Layout:
    if not isinstance(data, dict):
        raise InputError('Root must be an object')
    for key in ('width', 'height', 'footprint', 'start', 'goal', 'permanent', 'movable'):
        if key not in data:
            raise InputError('Missing required field: ' + key)
    width = integer(data['width'], 'width', 1, 30)
    height = integer(data['height'], 'height', 1, 30)
    footprint = pair(data['footprint'], 'footprint', 1, 30)
    start, goal = pair(data['start'], 'start'), pair(data['goal'], 'goal')
    margin = integer(data.get('margin_cells', 0), 'margin_cells', 0, 3)
    def cells(values: Any, name: str) -> frozenset[Cell]:
        if not isinstance(values, list):
            raise InputError(name + ' must be a list')
        result = [pair(v, name) for v in values]
        if len(result) != len(set(result)):
            raise InputError(name + ' has duplicate cells')
        if any(x >= width or y >= height for x, y in result):
            raise InputError(name + ' has cells outside the grid')
        return frozenset(result)
    permanent = cells(data['permanent'], 'permanent')
    raw = data['movable']
    if not isinstance(raw, list) or len(raw) > 6:
        raise InputError('movable must be a list with at most 6 objects')
    movable: list[tuple[str, frozenset[Cell]]] = []
    ids: set[str] = set()
    all_cells = set(permanent)
    for obj in raw:
        if not isinstance(obj, dict) or 'id' not in obj or 'cells' not in obj:
            raise InputError('Each movable object requires id and cells')
        name = obj['id']
        if not isinstance(name, str) or not name.strip() or len(name) > 80 or name in ids:
            raise InputError('Movable IDs must be unique nonempty strings, max 80 characters')
        body = cells(obj['cells'], name)
        if not body or all_cells.intersection(body):
            raise InputError('Movable cells must be nonempty and cannot overlap other objects')
        ids.add(name)
        all_cells.update(body)
        movable.append((name, body))
    layout = Layout(width, height, footprint, start, goal, permanent,
                    tuple(sorted(movable)), margin)
    if not valid_area(layout, start) or not valid_area(layout, goal):
        raise InputError('Start or goal footprint, including margin, is outside the grid')
    if occupied(layout, start).intersection(all_cells):
        raise InputError('The initial footprint, including margin, intersects an obstacle')
    return layout


def solve(layout: Layout) -> dict[str, Any]:
    """Lexicographic optimum: unique removable-object count, then grid steps.

    State = (anchor x, anchor y, encountered movable-object bitmask). Each
    nonnegative edge grows the mask monotonically and adds one step. Dijkstra
    therefore returns the exact optimum for this small, fixed-orientation model.
    """
    assumptions = [
        'Synthetic or manually supplied discrete 2D layout; completeness is not certified.',
        'Fixed rectangular footprint; no rotation, height, weight, cables, or lifting.',
        'Cardinal one-cell moves only; goal means an interior destination anchor, not a physical exit.',
        'All encountered movable objects can be removed off-plan beforehand; feasibility of moving them is not checked.',
        'Clearance margin is a user-specified integer, not a safety recommendation.',
        'No physical safety, regulatory compliance, or real-world path feasibility guarantee.'
    ]
    start = (*layout.start, 0)
    distances = {start: 0}
    previous: dict[tuple[int,int,int], tuple[int,int,int]] = {}
    queue = [(0, 0, *start)]
    explored = 0
    while queue:
        count, steps, x, y, mask = heapq.heappop(queue)
        state = (x, y, mask)
        if distances.get(state) != steps:
            continue
        explored += 1
        if (x, y) == layout.goal:
            route = []
            node = state
            while True:
                route.append([node[0], node[1]])
                if node == start:
                    break
                node = previous[node]
            route.reverse()
            names = [name for i, (name, _) in enumerate(layout.movable) if mask & (1 << i)]
            return dict(status='ROUTE_IN_MODEL', relocation_count=len(names),
                        remove_before_route=names, steps=steps, path=route,
                        explored_states=explored, assumptions=assumptions)
        for dx, dy in ((1,0),(0,1),(-1,0),(0,-1)):
            pos = (x + dx, y + dy)
            if not valid_area(layout, pos):
                continue
            body = occupied(layout, pos)
            if body & layout.permanent:
                continue
            new_mask = mask
            for i, (_, obstruction) in enumerate(layout.movable):
                if body & obstruction:
                    new_mask |= 1 << i
            next_state = (*pos, new_mask)
            if steps + 1 < distances.get(next_state, sys.maxsize):
                distances[next_state] = steps + 1
                previous[next_state] = state
                heapq.heappush(queue, (new_mask.bit_count(), steps+1, *next_state))
    return dict(status='NO_ROUTE_IN_MODEL', relocation_count=None,
                remove_before_route=[], steps=None, path=[],
                explored_states=explored, assumptions=assumptions)


def evaluate(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        missing = [k for k in ('width','height','footprint','start','goal','permanent','movable')
                   if k not in data]
        if missing:
            return {'status': 'INSUFFICIENT_INPUT', 'missing_fields': missing, 'path': []}
    return solve(load_layout(data))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('layout', type=Path)
    args = parser.parse_args()
    try:
        if args.layout.stat().st_size > 1_000_000:
            raise InputError('Input larger than 1 MB')
        data = json.loads(args.layout.read_text(encoding='utf-8'))
        result = evaluate(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 2 if result['status'] == 'INSUFFICIENT_INPUT' else 0
    except (OSError, ValueError, RecursionError) as exc:
        print(json.dumps({'status': 'INVALID_INPUT', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
