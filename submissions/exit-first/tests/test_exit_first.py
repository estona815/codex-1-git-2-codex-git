"""Independent subset-enumeration oracle and seeded synthetic cases."""
import copy
import random
import unittest
from collections import deque
from exit_first import evaluate, InputError


def base():
    return dict(width=8, height=5, footprint=[2,2], start=[0,1], goal=[6,1],
                permanent=[], movable=[], margin_cells=0)


def oracle(d):
    """Independent: enumerate objects removed, then ordinary 2D BFS.

    Deliberately does not import engine geometry/validation/search functions.
    """
    best = None
    n = len(d['movable'])
    for mask in range(1 << n):
        blocks = set(map(tuple, d['permanent']))
        for i, obj in enumerate(d['movable']):
            if not mask & (1 << i):
                blocks.update(map(tuple, obj['cells']))
        m = d.get('margin_cells', 0)
        fw, fh = d['footprint']
        def free(x,y):
            if x-m < 0 or y-m < 0 or x+fw+m > d['width'] or y+fh+m > d['height']:
                return False
            return all((xx,yy) not in blocks for xx in range(x-m,x+fw+m)
                       for yy in range(y-m,y+fh+m))
        start, goal = tuple(d['start']), tuple(d['goal'])
        seen = {start}
        q = deque([(start,0)])
        while q:
            (x,y), steps = q.popleft()
            if (x,y) == goal:
                score = (mask.bit_count(), steps)
                if best is None or score < best:
                    best = score
                break
            for nx, ny in ((x+1,y),(x,y+1),(x-1,y),(x,y-1)):
                if (nx,ny) not in seen and free(nx,ny):
                    seen.add((nx,ny)); q.append(((nx,ny),steps+1))
    return best


def assert_path(test, d, result):
    if result['status'] != 'ROUTE_IN_MODEL':
        test.assertEqual(result['path'], []); return
    test.assertEqual(result['path'][0], d['start'])
    test.assertEqual(result['path'][-1], d['goal'])
    test.assertEqual(len(result['path'])-1, result['steps'])
    forbidden = set(map(tuple,d['permanent']))
    for obj in d['movable']:
        if obj['id'] not in result['remove_before_route']:
            forbidden.update(map(tuple,obj['cells']))
    fw,fh = d['footprint']; m=d.get('margin_cells',0)
    for i,(x,y) in enumerate(result['path']):
        test.assertGreaterEqual(x-m,0);test.assertGreaterEqual(y-m,0)
        test.assertLessEqual(x+fw+m,d['width']);test.assertLessEqual(y+fh+m,d['height'])
        for xx in range(x-m,x+fw+m):
            for yy in range(y-m,y+fh+m): test.assertNotIn((xx,yy), forbidden)
        if i:
            px,py=result['path'][i-1]
            test.assertEqual(abs(x-px)+abs(y-py),1)

class PlannerTests(unittest.TestCase):
    def test_open_route(self):
        d=base(); r=evaluate(d);self.assertEqual((r['relocation_count'],r['steps']),(0,6));assert_path(self,d,r)
    def test_required_removal(self):
        d=base();d['movable']=[dict(id='shelf-A',cells=[[3,y] for y in range(5)])]
        r=evaluate(d);self.assertEqual(r['remove_before_route'],['shelf-A']);assert_path(self,d,r)
    def test_permanent_barrier(self):
        d=base();d['permanent']=[[3,y] for y in range(5)]
        self.assertEqual(evaluate(d)['status'],'NO_ROUTE_IN_MODEL')
    def test_no_removal_preferred_to_shorter_path(self):
        d=dict(width=7,height=5,footprint=[1,1],start=[0,2],goal=[6,2],
               permanent=[],movable=[dict(id='box',cells=[[3,2]])])
        r=evaluate(d);self.assertEqual((r['relocation_count'],r['steps']),(0,8));assert_path(self,d,r)
    def test_same_object_counted_once(self):
        d=base();d['movable']=[dict(id='long-shelf',cells=[[3,y] for y in range(5)]+[[4,y] for y in range(5)])]
        self.assertEqual(evaluate(d)['relocation_count'],1)
    def test_goal_equals_start(self):
        d=base();d['goal']=d['start'][:];self.assertEqual(evaluate(d)['steps'],0)
    def test_missing_not_infeasible(self):
        d=base();del d['footprint'];self.assertEqual(evaluate(d)['status'],'INSUFFICIENT_INPUT')
    def test_bad_number(self):
        for bad in (True,0,-1,31,3.5,'8'):
            d=base();d['width']=bad
            with self.subTest(bad=bad),self.assertRaises(InputError):evaluate(d)
    def test_start_collision(self):
        d=base();d['permanent']=[[0,1]]
        with self.assertRaises(InputError):evaluate(d)
    def test_overlapping_obstacles(self):
        d=base();d['permanent']=[[3,3]];d['movable']=[dict(id='bad',cells=[[3,3]])]
        with self.assertRaises(InputError):evaluate(d)
    def test_duplicate_ids(self):
        d=base();d['movable']=[dict(id='same',cells=[[3,3]]),dict(id='same',cells=[[4,3]])]
        with self.assertRaises(InputError):evaluate(d)
    def test_out_of_bounds(self):
        d=base();d['permanent']=[[8,2]]
        with self.assertRaises(InputError):evaluate(d)
    def test_input_not_mutated(self):
        d=base();saved=copy.deepcopy(d);evaluate(d);self.assertEqual(d,saved)
    def test_deterministic(self):
        d=base();self.assertEqual(evaluate(d),evaluate(d))
    def test_margin_is_applied(self):
        d=dict(width=7,height=5,footprint=[1,1],start=[1,2],goal=[5,2],
               permanent=[[3,0],[3,1],[3,3],[3,4]],movable=[],margin_cells=0)
        self.assertEqual(evaluate(d)['status'],'ROUTE_IN_MODEL')
        d['margin_cells']=1;self.assertEqual(evaluate(d)['status'],'NO_ROUTE_IN_MODEL')
    def test_200_seeded_layouts_against_independent_oracle(self):
        rng=random.Random(20260922)
        for case in range(200):
            w=h=6; fw,fh=rng.choice([(1,1),(2,1),(1,2),(2,2)])
            start=[0,0];goal=[w-fw,h-fh]
            protected={(x,y) for x in range(fw) for y in range(fh)}
            options=[(x,y) for x in range(w) for y in range(h) if (x,y) not in protected]
            rng.shuffle(options)
            permanent=options[:rng.randrange(0,9)];rest=[v for v in options if v not in permanent]
            movable=[dict(id=f'object-{i}',cells=[list(v)]) for i,v in enumerate(rest[:3])]
            d=dict(width=w,height=h,footprint=[fw,fh],start=start,goal=goal,
                   permanent=[list(v) for v in permanent],movable=movable)
            with self.subTest(case=case):
                r=evaluate(d);expected=oracle(d)
                actual=None if r['status']=='NO_ROUTE_IN_MODEL' else (r['relocation_count'],r['steps'])
                self.assertEqual(actual,expected);assert_path(self,d,r)

if __name__=='__main__': unittest.main()
