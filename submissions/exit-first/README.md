# EXIT FIRST

Before equipment goes in, examine the conditions for moving it again.

This is a new, standalone HACK47: OFFGRID entry, developed on 22 September 2026. It is stored in an isolated submission directory and branch of the author's general workspace. Other files in this repository are unrelated and are not part of this entry. The repository's main branch has not been changed by this publication.

## What works

An offline Python command-line prototype accepts a complete small 2D grid, a fixed rectangular equipment footprint, start and target anchors, permanent obstacles, and up to six removable objects. It minimizes **distinct objects assumed removed before the route**, then movement steps. It returns the route and removal set, no route within the model, or insufficient input. It never fills missing equipment dimensions with a guess.

This is not a floor-plan reader, relocation work order, physical exit certificate or commercial SaaS.

## Run in under a minute (Python 3.10+)

No third-party packages, API key, model download or cloud account is required.

```sh
git clone --branch hack47-exit-first-20260922 --single-branch https://github.com/estona815/codex-1-git-2-codex-git.git exit-first-workspace
cd exit-first-workspace/submissions/exit-first
python3 -m unittest discover -s tests -v
python3 demo.py
```

To use a custom layout, save this as `layout.json` and run `python3 exit_first.py layout.json`:

```json
{"width":8,"height":5,"footprint":[2,2],"start":[0,1],"goal":[6,1],"permanent":[],"movable":[{"id":"shelf-A","cells":[[3,0],[3,1],[3,2],[3,3],[3,4]]}],"margin_cells":0}
```

Grid limits: 30 by 30, at most six removable objects, footprint dimensions from 1 to 30 cells, optional integer margin 0 to 3. Margin is user input, not a recommended safety clearance. Missing fields produce INSUFFICIENT_INPUT; contradictory/invalid inputs fail validation. CLI reads at most 1 MB and returns exit code 2 for invalid or insufficient input.

## Five executable demonstrations

`demo.py` computes these at runtime; it does not substitute recorded answers.

| Synthetic case | Actual result | Removed objects | Steps |
|---|---|---:|---:|
| Open space, 2x2 footprint | ROUTE_IN_MODEL | 0 | 6 |
| Same space, shelf across the route | ROUTE_IN_MODEL | shelf-A (1) | 6 |
| Shelf replaced by fixed wall | NO_ROUTE_IN_MODEL | N/A | N/A |
| Footprint omitted | INSUFFICIENT_INPUT | N/A | N/A |
| 1x1 footprint, avoid one box by detouring | ROUTE_IN_MODEL | 0 | 8 |

The last case demonstrates the objective: it takes an eight-step route that removes nothing rather than a six-step route requiring one removal. The shelf case assumes the entire shelf has already been removed off-plan; it does not drive equipment through an occupied shelf.

The terminal illustration shows route anchors, not swept-footprint boundaries. Geometry checks use the full footprint and supplied margin.

## Algorithm

The search state is `(x, y, encountered_object_bitmask)`. Four-connected moves grow the mask monotonically. A lexicographic Dijkstra priority `(number_of_set_bits, steps, x, y, mask)` yields a minimum-removal-set route, then a shortest route for that objective. Distances and predecessor maps are maintained for the full state, not just the cell. The bounded state count is at most `30*30*2^6 = 57,600`; footprint collision work and queue overhead are additional. This is an engineering bound, not a measured runtime or concurrency claim.

## Verification performed on 2026-09-22

16 unittest methods passed. One method independently enumerates all subsets of removable objects and uses ordinary breadth-first search, comparing optimum and path validity on 200 seeded synthetic 6x6 layouts. Returned routes are checked for endpoints, continuity, bounds, and collisions against all obstacles not removed. Other tests cover repeated object counting, detour preference, margin behavior, missing data, invalid numbers, overlapping obstacles, duplicate IDs, input immutability and determinism.

Actual rerun: `Ran 16 tests in 0.105s` / `OK`. This timing is from one small local test run, not a product performance promise. `python3 -m py_compile exit_first.py demo.py tests/test_exit_first.py` also completed successfully.

## Limits and intended use

All inputs must be interpreted as a simplified model. Fixed orientation only; no rotation, continuous space, height, weight, ramps, cables, pipes, lifting, deformation or worker-space assessment. Every identified removable object is assumed removable off-plan before the route starts; its own movement feasibility is not evaluated. The target is an interior anchor, not full extraction from a building. Infeasibility in this discrete model does not prove physical infeasibility; a found route does not establish physical safety or compliance.

The proposed first user is a small-equipment vendor or layout reviewer. No customer interviews, deployments, revenue, labor savings or physical trials are claimed. A next step would be expert validation of inputs and a measured comparison against manual model review, before any real facility application.

## AI disclosure and authorship

ChatGPT generated and revised the new engine, tests, demo and documentation under the participant's direction and submission authorization. Automated local tests were actually run. No unaided human authorship is claimed. The path calculation itself is deterministic Python and makes no LLM or network calls. It uses only the Python standard library. Existing workspace files, prior competition entries and private personal documents were not reused as this project's code.

## Rights

Published for hackathon inspection and evaluation. No additional general-purpose open-source license is granted in this repository entry. Participant/organizer rights remain governed by the applicable hackathon and platform terms. No physical-safety warranty is given.
