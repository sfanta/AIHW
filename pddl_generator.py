def generate_pddl(env, state, output_filename="problem.pddl"):
    """
    Translates the current RicochetEnvironment and State into a PDDL problem file.
    Includes Boundary detection for edges.
    """
    with open(output_filename, "w") as f:
        f.write("(define (problem ricochet-instance)\n")
        f.write("  (:domain ricochet)\n")
        
        # 1. Objects
        f.write("  (:objects \n")
        robots = [f"r{i}" for i in range(len(state.robots))]
        f.write(f"    {' '.join(robots)} - robot\n")
        
        cells = []
        for x in range(env.size):
            for y in range(env.size):
                cells.append(f"c_{x}_{y}")
        f.write(f"    {' '.join(cells)} - cell\n")
        
        f.write("    north south east west - direction\n")
        f.write("  )\n\n")
        
        # 2. Init State
        f.write("  (:init \n")
        
        # Robot Positions
        for i, (rx, ry) in enumerate(state.robots):
            f.write(f"    (at r{i} c_{rx}_{ry})\n")
            f.write(f"    (occupied c_{rx}_{ry})\n")
            f.write(f"    (idle r{i})\n")
            
        # Grid Topology & Boundaries
        for x in range(env.size):
            for y in range(env.size):
                # North (y-1)
                if y > 0: 
                    f.write(f"    (next c_{x}_{y} c_{x}_{y-1} north)\n")
                else:
                    f.write(f"    (boundary c_{x}_{y} north)\n") # Hit top edge
                
                # South (y+1)
                if y < env.size - 1: 
                    f.write(f"    (next c_{x}_{y} c_{x}_{y+1} south)\n")
                else:
                    f.write(f"    (boundary c_{x}_{y} south)\n") # Hit bottom edge
                
                # West (x-1)
                if x > 0: 
                    f.write(f"    (next c_{x}_{y} c_{x-1}_{y} west)\n")
                else:
                    f.write(f"    (boundary c_{x}_{y} west)\n") # Hit left edge
                    
                # East (x+1)
                if x < env.size - 1: 
                    f.write(f"    (next c_{x}_{y} c_{x+1}_{y} east)\n")
                else:
                    f.write(f"    (boundary c_{x}_{y} east)\n") # Hit right edge

        # Walls (Blocked)
        for (wx, wy), direction in env.walls:
            nx, ny = -1, -1
            if direction == "north": nx, ny = wx, wy - 1
            elif direction == "south": nx, ny = wx, wy + 1
            elif direction == "east": nx, ny = wx + 1, wy
            elif direction == "west": nx, ny = wx - 1, wy
            
            if 0 <= nx < env.size and 0 <= ny < env.size:
                f.write(f"    (blocked c_{wx}_{wy} c_{nx}_{ny})\n")

        f.write("  )\n\n")
        
        # 3. Goal
        gx, gy = env.goal_pos
        f.write("  (:goal \n")
        f.write(f"    (and (at r{env.target_idx} c_{gx}_{gy}) (idle r{env.target_idx}))\n")
        f.write("  )\n")
        f.write(")\n")

    return output_filename