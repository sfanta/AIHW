import time
import random
import csv
import re
import os
import sys
import subprocess
from ricochet_model import RicochetEnvironment, RicochetState
from astar_solver import AStarSolver
from pddl_generator import generate_pddl
from main import parse_pddl_plan  # Reuse the parser from main

# ==========================================
# CONFIGURATION
# ==========================================
# UPDATE THIS to match your main.py path
PLANNER_PATH = "/Users/andrea/Documents/GitHub/AIHW/fast_downward/fast-downward.py"
OUTPUT_CSV = "experiment_results.csv"

# ==========================================
# 1. RANDOM INSTANCE GENERATOR
# ==========================================
def generate_random_instance(size, num_walls, num_robots=2, seed=None):
    if seed: random.seed(seed)
    
    # 1. Generate Walls
    # We simple-mindedly place walls between cells
    walls = set()
    while len(walls) < num_walls:
        rx = random.randint(0, size-1)
        ry = random.randint(0, size-1)
        direction = random.choice(['north', 'south', 'east', 'west'])
        
        # Avoid blocking the edges (already boundaries)
        if direction == 'north' and ry == 0: continue
        if direction == 'south' and ry == size-1: continue
        if direction == 'west' and rx == 0: continue
        if direction == 'east' and rx == size-1: continue
        
        walls.add(((rx, ry), direction))
        
        # Add the reciprocal wall to make it solid from both sides
        if direction == 'north': walls.add(((rx, ry-1), 'south'))
        elif direction == 'south': walls.add(((rx, ry+1), 'north'))
        elif direction == 'east': walls.add(((rx+1, ry), 'west'))
        elif direction == 'west': walls.add(((rx-1, ry), 'east'))

    # 2. Generate Robots
    positions = set()
    while len(positions) < num_robots:
        positions.add((random.randint(0, size-1), random.randint(0, size-1)))
    robots = list(positions)
    
    # 3. Goal
    # Pick a random spot that isn't the start of the target robot
    while True:
        gx, gy = (random.randint(0, size-1), random.randint(0, size-1))
        if (gx, gy) != robots[0]:
            goal_pos = (gx, gy)
            break
            
    env = RicochetEnvironment(size, walls, goal_pos, target_robot_index=0)
    state = RicochetState(robots)
    return env, state

# ==========================================
# 2. RUNNERS
# ==========================================

def run_astar_experiment(env, state):
    #def heuristic(s, e):
    #    # Manhattan                            heuleristic semplice e stupida
    #    tx, ty = s.robots[e.target_idx]
    #    gx, gy = e.goal_pos
    #    return abs(tx - gx) + abs(ty - gy)
    def heuristic_bfs(state, env):
        # Calculate true distance on the grid considering walls, 
        # but ignoring other robots (Relaxed Problem)
        # This is much stronger than Manhattan but costlier to compute.
        tx, ty = state.robots[env.target_idx]
        gx, gy = env.goal_pos
        
        # Simple BFS from (tx, ty) to (gx, gy) using env walls
        queue = [(tx, ty, 0)]
        visited = set([(tx, ty)])
        
        while queue:
            cx, cy, dist = queue.pop(0)
            if (cx, cy) == (gx, gy):
                return dist
                
            # Try all 4 sliding moves (ignoring other robots!)
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = env._slide(cx, cy, dx, dy, []) # Pass empty list for robots
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, dist + 1))
                    
        return float('inf')

    solver = AStarSolver(env, heuristic_bfs)
    try:
        # Set a reasonable timeout inside your solver if possible, 
        # or just hope it finishes for small boards
        res = solver.solve(state)
        if res:
            return {
                "astar_time": res['time'],
                "astar_expanded": res['expanded'],
                "astar_cost": len(res['path']) - 1
            }
    except Exception as e:
        print(f"A* Error: {e}")
    
    return {"astar_time": "TIMEOUT", "astar_expanded": 0, "astar_cost": 0}

def run_pddl_experiment(env, state):
    # Reuse logic from main.py but parse more metrics
    domain_file = "domain.pddl"
    prob_file = "experiment_prob.pddl"
    generate_pddl(env, state, prob_file)
    
    cmd = [
        sys.executable, PLANNER_PATH,
        "--alias", "seq-opt-lmcut",
        domain_file, prob_file
    ]
    
    start_t = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_t
    
    if os.path.exists("sas_plan"):
        # Read plan length
        with open("sas_plan") as f:
            plan = parse_pddl_plan(f.read())
        os.remove("sas_plan")
        
        # PARSE OUTPUT FOR "EXPANDED STATES"
        # Fast Downward usually prints: "Expanded X state(s)."
        expanded = 0
        match = re.search(r"Expanded (\d+) state", result.stdout)
        if match:
            expanded = int(match.group(1))
            
        return {
            "pddl_time": duration,
            "pddl_expanded": expanded,
            "pddl_cost": len(plan) # This is micro-steps (slide start/move/stop)
        }
    return {"pddl_time": "TIMEOUT", "pddl_expanded": 0, "pddl_cost": 0}

# ==========================================
# 3. MAIN LOOP
# ==========================================
if __name__ == "__main__":
    # Ensure domain exists
    if not os.path.exists("domain.pddl"):
        print("Please run this from the folder containing domain.pddl")
        sys.exit(1)

    print(f"Starting Experiments... saving to {OUTPUT_CSV}")
    
    with open(OUTPUT_CSV, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["GridSize", "Walls", "AStar_Time", "AStar_Expanded", "PDDL_Time", "PDDL_Expanded"])
        
        # SCALING PARAMETER: Grid Size (N)
        # We start small (5) and go up.
        # Warning: A* gets slow very fast on large empty grids.
        for size in [5, 6, 7, 8, 9, 10]: 
            # Run 3 random instances per size to get an average
            for i in range(3):
                print(f"\n--- Running Size {size}x{size} (Iter {i+1}) ---")
                
                # Create instance (Walls scale with size, approx size*2)
                env, state = generate_random_instance(size, num_walls=size*2, seed=i*size)
                
                # Run A*
                print("  Running A*...")
                astar_res = run_astar_experiment(env, state)
                
                # Run PDDL
                print("  Running Planner...")
                pddl_res = run_pddl_experiment(env, state)
                
                # Write row
                writer.writerow([
                    size, 
                    size*2,
                    astar_res["astar_time"],
                    astar_res["astar_expanded"],
                    pddl_res["pddl_time"],
                    pddl_res["pddl_expanded"]
                ])
                
                print(f"  Result: A*={astar_res['astar_time']}s, PDDL={pddl_res['pddl_time']}s")
                csvfile.flush() # Save progress immediately

    print("\nExperiments Completed")