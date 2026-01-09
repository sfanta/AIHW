import sys
import os
import time
import subprocess

# Import your modules
from ricochet_model import RicochetEnvironment, RicochetState
from astar_solver import AStarSolver
from pddl_generator import generate_pddl

# ==========================================
# CONFIGURATION
# ==========================================
# UPDATE THIS PATH to where your fast-downward.py is located.
# Example: "./fast_downward/fast-downward.py" or "/home/user/downward/fast-downward.py"
PLANNER_PATH = "/Users/andrea/Documents/GitHub/AIHW/fast_downward/fast-downward.py" 

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def create_simple_scenario():
    """
    Creates a 5x5 test grid.
    Target Robot (Index 0) starts at (0,0).
    Goal is (4,4).
    Helper Robot (Index 1) starts at (4,0).
    """
    size = 5
    goal_pos = (4, 4)
    
    # Walls defined as ((x, y), direction_blocked)
    walls = {
        ((4, 3), 'south'), # Wall blocking entry to goal from North
        ((4, 4), 'north'), # Reciprocal wall
        ((2, 2), 'east'),  # Obstacle in middle
        ((3, 2), 'west')
    }
    
    # Robot 0 (Target) at (0,0)
    # Robot 1 (Helper) at (4,0)
    initial_robots = [(0, 0), (4, 0)] 
    
    env = RicochetEnvironment(size, walls, goal_pos, target_robot_index=0)
    start_state = RicochetState(initial_robots)
    
    return env, start_state

# def manhattan_heuristic(state, env):
#     """
#     Admissible heuristic: Manhattan distance from target robot to goal.
#     Ignores walls and sliding constraints.
#     """
#     tx, ty = state.robots[env.target_idx]
#     gx, gy = env.goal_pos
#     return abs(tx - gx) + abs(ty - gy)
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
def solve_with_pddl(env, start_state):
    """
    1. Generates problem.pddl
    2. Runs Fast Downward
    3. Parses output
    """
    domain_filename = "domain.pddl"
    problem_filename = "problem.pddl"
    
    # 1. Generate the specific problem file
    print(f"Generating {problem_filename}...")
    generate_pddl(env, start_state, output_filename=problem_filename)
    
    # Check if planner exists
    if not os.path.exists(PLANNER_PATH):
        print(f"\n[ERROR] Planner executable not found at: {PLANNER_PATH}")
        print("Please edit the PLANNER_PATH variable in 'main.py' to point to your installation.")
        return None

    # 2. Construct the command
    # Using 'seq-opt-lmcut' alias which is optimal (A*)
    cmd = [
        sys.executable, # Uses the current python interpreter
        PLANNER_PATH,
        "--alias", "seq-opt-lmcut", 
        domain_filename,
        problem_filename
    ]
    
    print(f"Running Planner command: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        # Run subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        # 3. Check results
        if result.returncode != 0:
            print("Planner returned non-zero exit code.")
            print(result.stderr) # Uncomment to debug planner errors
        
        # Fast Downward writes solution to 'sas_plan'
        if os.path.exists("sas_plan"):
            print(f"Planner finished in {duration:.4f}s")
            with open("sas_plan", "r") as f:
                plan_content = f.read()
            os.remove("sas_plan") # Clean up
            return parse_pddl_plan(plan_content)
        else:
            print("No 'sas_plan' file generated. Solution likely not found.")
            return None
            
    except Exception as e:
        print(f"An error occurred while running planner: {e}")
        return None

def parse_pddl_plan(plan_str):
    """
    Converts PDDL output string into a readable list of steps.
    """
    steps = []
    lines = plan_str.strip().splitlines()
    for line in lines:
        if line.startswith(";") or not line.strip(): 
            continue
        # Remove parens and split
        # e.g. "(move-slide r0 c_0_0 c_0_4 east)" -> "move-slide r0..."
        clean = line.strip("() ")
        steps.append(clean)
    return steps

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    print("=== Ricochet Robots Solver Pipeline ===\n")
    
    # 1. Setup
    env, start_state = create_simple_scenario()
    print(f"Goal Position: {env.goal_pos}")
    print(f"Robots Start : {start_state.robots}")
    print("-" * 40)

    # 2. Run Task 2.1: A*
    print("\n>>> Task 2.1: Running Custom A* Solver...")
    astar = AStarSolver(env, heuristic_bfs)
    astar_result = astar.solve(start_state)
    
    if astar_result:
        print("A* SUCCESS!")
        print(f"Time: {astar_result['time']:.4f}s")
        print(f"Nodes Expanded: {astar_result['expanded']}")
        print(f"Path Length: {len(astar_result['path'])}")
        print("Path Steps:")
        for i, s in enumerate(astar_result['path']):
            print(f"  {i}: {s.robots}")
    else:
        print("A* FAILED to find a solution.")

    print("-" * 40)

    # 3. Run Task 2.2: PDDL Planner
    print("\n>>> Task 2.2: Running PDDL Planner...")
    
    # Verify domain.pddl exists
    if not os.path.exists("domain.pddl"):
        print("[ERROR] 'domain.pddl' not found in current directory.")
    else:
        pddl_plan = solve_with_pddl(env, start_state)
        
        if pddl_plan:
            print("PDDL SUCCESS!")
            print(f"Plan Length: {len(pddl_plan)}")
            print("Plan Steps:")
            for step in pddl_plan:
                print(f"  {step}")
        else:
            print("PDDL FAILED or Planner not configured.")