def generate_pddl(env, state, output_filename="problem.pddl"):
    """
    Translates the current RicochetEnvironment and State into a PDDL problem file.
    """
    with open(output_filename, "w") as f:
        f.write("(define (problem ricochet-instance)\n")
        f.write("  (:domain ricochet)\n")
        
        # 1. Objects
        f.write("  (:objects \n")
        # Robots
        robots = [f"r{i}" for i in range(len(state.robots))]
        f.write(f"    {' '.join(robots)} - robot\n")
        
        # Cells (e.g., c_0_0, c_0_1...)
        cells = []
        for x in range(env.size):
            for y in range(env.size):
                cells.append(f"c_{x}_{y}")
        f.write(f"    {' '.join(cells)} - cell\n")
        
        # Directions
        f.write("    north south east west - direction\n")
        f.write("  )\n\n")
        
        # 2. Init State
        f.write("  (:init \n")
        
        # Robot Positions
        for i, (rx, ry) in enumerate(state.robots):
            f.write(f"    (at r{i} c_{rx}_{ry})\n")
            f.write(f"    (occupied c_{rx}_{ry})\n")
            f.write(f"    (idle r{i})\n")
            
        # Grid Topology (Adjacency)
        # We generate (next c_x_y c_next_x_next_y direction)
        for x in range(env.size):
            for y in range(env.size):
                # North (y-1)
                if y > 0: f.write(f"    (next c_{x}_{y} c_{x}_{y-1} north)\n")
                # South (y+1)
                if y < env.size - 1: f.write(f"    (next c_{x}_{y} c_{x}_{y+1} south)\n")
                # West (x-1)
                if x > 0: f.write(f"    (next c_{x}_{y} c_{x-1}_{y} west)\n")
                # East (x+1)
                if x < env.size - 1: f.write(f"    (next c_{x}_{y} c_{x+1}_{y} east)\n")

        # Walls (Blocked)
        # Assuming env.walls is a set of ((x, y), direction)
        # Note: In PDDL we need to block the specific link between cells
        for (wx, wy), direction in env.walls:
            # Logic to find the neighbor cell based on direction
            nx, ny = -1, -1
            if direction == "north": nx, ny = wx, wy - 1
            elif direction == "south": nx, ny = wx, wy + 1
            elif direction == "east": nx, ny = wx + 1, wy
            elif direction == "west": nx, ny = wx - 1, wy
            
            if 0 <= nx < env.size and 0 <= ny < env.size:
                f.write(f"    (blocked c_{wx}_{wy} c_{nx}_{ny})\n")

        f.write("  )\n\n")
        
        # 3. Goal
        # Target robot (index 0) must reach goal_pos
        gx, gy = env.goal_pos
        f.write("  (:goal \n")
        f.write(f"    (and (at r{env.target_idx} c_{gx}_{gy}) (idle r{env.target_idx}))\n")
        f.write("  )\n")
        f.write(")\n")

    return output_filename