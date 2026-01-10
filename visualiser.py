import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import random
import sys
import os

# Import your existing modules
from ricochet_model import RicochetEnvironment, RicochetState
from pddl_generator import generate_pddl
from main import solve_with_pddl, create_simple_scenario

# ==========================================
# CONFIGURATION
# ==========================================
# Update this to match your main.py
PLANNER_PATH = "/Users/andrea/Documents/GitHub/AIHW/fast_downward/fast-downward.py"

# ==========================================
# PARSER LOGIC
# ==========================================
def parse_plan_to_states(env, start_state, plan_steps):
    """
    Converts a PDDL plan (list of strings) into a sequence of robot coordinates
    for animation.
    """
    # Map 'c_x_y' string to (x, y) tuple
    def parse_cell(c_str):
        parts = c_str.split('_')
        return int(parts[1]), int(parts[2])

    # Map 'r0', 'r1' to integer indices
    def parse_robot(r_str):
        return int(r_str.replace('r', ''))

    current_robots = list(start_state.robots)
    history = [list(current_robots)] # Frame 0

    for step in plan_steps:
        # Step format examples:
        # "start-slide r0 c_0_0 c_0_1 south" (No visual move yet)
        # "move-slide r0 c_0_0 c_0_1 south"  (Visual move!)
        # "stop-slide-wall r0 ..."           (No visual move)
        
        parts = step.split()
        action = parts[0]
        
        if action == "move-slide":
            r_idx = parse_robot(parts[1])
            to_cell = parse_cell(parts[3]) # The destination of this micro-step
            
            # Update position
            current_robots[r_idx] = to_cell
            
            # Add a copy of the current positions to history
            history.append(list(current_robots))
            
    return history

# ==========================================
# VISUALIZATION LOGIC
# ==========================================
def animate_ricochet(env, history, title="Ricochet Solution"):
    """
    Creates a Matplotlib animation of the solution.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 1. Setup Grid
    ax.set_xlim(-0.5, env.size - 0.5)
    ax.set_ylim(env.size - 0.5, -0.5) # Invert Y so (0,0) is top-left
    ax.set_xticks(range(env.size))
    ax.set_yticks(range(env.size))
    ax.grid(True, color='lightgray', linestyle='-')
    ax.set_aspect('equal')
    
    # 2. Draw Static Walls
    # Wall logic: if wall at (x,y) facing 'south', draw line between (x, y+1) and (x+1, y+1)
    # Note: Our coordinates are centers. Grid lines are at +0.5 / -0.5
    for (wx, wy), direction in env.walls:
        if direction == 'north':
            ax.plot([wx-0.5, wx+0.5], [wy-0.5, wy-0.5], color='black', linewidth=3)
        elif direction == 'south':
            ax.plot([wx-0.5, wx+0.5], [wy+0.5, wy+0.5], color='black', linewidth=3)
        elif direction == 'east':
            ax.plot([wx+0.5, wx+0.5], [wy-0.5, wy+0.5], color='black', linewidth=3)
        elif direction == 'west':
            ax.plot([wx-0.5, wx-0.5], [wy-0.5, wy+0.5], color='black', linewidth=3)

    # 3. Draw Goal
    gx, gy = env.goal_pos
    goal_patch = patches.Rectangle((gx-0.5, gy-0.5), 1, 1, color='gold', alpha=0.3)
    ax.add_patch(goal_patch)
    ax.text(gx, gy, "GOAL", ha='center', va='center', fontsize=8, fontweight='bold', color='goldenrod')

    # 4. Initialize Robots (Circles)
    # Colors: Robot 0 (Target) is Red, others Blue
    colors = ['red'] + ['blue'] * (len(history[0]) - 1)
    robot_patches = []
    
    for i, (rx, ry) in enumerate(history[0]):
        circle = plt.Circle((rx, ry), 0.3, color=colors[i], ec='black')
        robot_patches.append(circle)
        ax.add_patch(circle)

    ax.set_title(title)

    # 5. Animation Update Function
    def update(frame_idx):
        positions = history[frame_idx]
        for i, (rx, ry) in enumerate(positions):
            robot_patches[i].center = (rx, ry)
        return robot_patches

    # Create Animation
    # interval=200ms means 5 steps per second
    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=150, blit=True, repeat=True)
    
    print("Close the window to exit script.")
    plt.show()

# ==========================================
# MAIN DRIVER
# ==========================================
if __name__ == "__main__":
    from experiments import generate_random_instance
    
    print("--- Ricochet Visualizer ---")
    
    # Option A: Visualise a Random Hard Board
    SIZE = 6
    print(f"Generating random {SIZE}x{SIZE} board...")
    # Seed 42 is usually a good predictable test
    env, start_state = generate_random_instance(SIZE, num_walls=10, seed=random.randint(0, 1000))
    
    # Option B: Use the simple 5x5 test case from before (Uncomment to use)
    # env, start_state = create_simple_scenario()

    print(f"Goal: {env.goal_pos}")
    print("Solving with PDDL (this may take a second)...")
    
    # We must patch the PLANNER_PATH in main if it wasn't set globally there
    import main
    main.PLANNER_PATH = PLANNER_PATH 
    
    # Run Solver
    plan = solve_with_pddl(env, start_state)
    
    if plan:
        print(f"Solution found! Steps: {len(plan)}")
        
        # Convert PDDL strings to Coordinate History
        history = parse_plan_to_states(env, start_state, plan)
        
        print(f"Animation has {len(history)} frames.")
        animate_ricochet(env, history, title=f"Ricochet Solution ({len(history)} micro-steps)")
    else:
        print("No solution found (or planner failed). Try running again for a different board.")